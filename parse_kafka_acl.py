import sys
import re
import argparse
from argparse import RawTextHelpFormatter

version = "1.0.0"


def create_parser():
    parser = argparse.ArgumentParser(
        description=('This script allows you to obtain access rules from Kafka ACL list in required format.\n\n'
                     'Rules may be filtered for next criteria:\n'
                     '- 1. Principal\n'
                     '- 2. Resource type\n'
                     '- 3. Resource name\n\n'),
        formatter_class=RawTextHelpFormatter
    )
    parser.add_argument('-f', '--file', help='File with a Kafka ACL list')
    parser.add_argument('-cn', '-CN', '--principal', '--user', default='.*?', help='Desired principal',
                        metavar='principal')

    parser.add_argument('-t', '--type',
                        choices=['TOPIC', 'GROUP', 'CLUSTER', 'TRANSACTIONAL_ID',
                                 'DELEGATION_TOKEN', 'UNKNOWN'],
                        type=str.upper, default=False,
                        help='Desired resource type',
                        metavar='resource_type')

    parser.add_argument('-n', '--name', default=False, help='Desired resource name',
                        metavar='resource_name')

    parser.add_argument('--pretty', action='store_true', help='Output in human-readable format')
    parser.add_argument('--usage', action='store_true', help='Print usage examples')
    parser.add_argument('--list', action='store_true',
                        help='Print type of resource which an ACL can be applied to')

    parser.add_argument('--version', action='version', help='Print version',
                        version='%(prog)s {}'.format(version))
    return parser


menu_parser = create_parser()
menu_args = menu_parser.parse_args(sys.argv[1:])


def print_resource_type_list():
    print('\nTypes of resource which an ACL can be applied to:\n\n'
          'CLUSTER\t\t\tThe cluster as a whole.\n'
          'DELEGATION_TOKEN\tA token ID.\n'
          'GROUP\t\t\tA consumer group.\n'
          'TOPIC\t\t\tA Kafka topic.\n'
          'TRANSACTIONAL_ID\tA transactional ID.\n'
          'UNKNOWN\t\t\tRepresents any ResourceType which this client '
          'cannot understand, perhaps because this client is too old.')
    exit()


def print_usage():
    print('\n1. Get ACLs for each principal and resource in human readable format:\n\n'
          'python parse_kafka_acl.py --file sample_list.txt --pretty\n\n'
          '2. Get ACLs for all topics for user with CN "testuser":\n\n'
          'python parse_kafka_acl.py --file sample_list.txt --principal testuser --type topic\n\n'
          '3. Get ACLs for all groups:\n\n'
          'python parse_kafka_acl.py --file sample_list.txt --type group\n\n'
          '4. Get ACLs for topic with name "kafka-topic1":\n\n'
          'python parse_kafka_acl.py --file sample_list.txt --type topic --name kafka-topic1\n\n'
          '5. Get ACLs for resources with name "*"\n\n'
          'python parse_kafka_acl.py --file sample_list.txt --name *')
    exit()


# acl_dict = {('resource_name_1','resource_type_1'): { 'name': 'resource_name_1',
#                                                      'type': 'TOPIC',
#                                                      1: {'principal': 'principal_1',
#                                                      'operation': 'operation_1',
#                                                      'permissionType': 'permissionType_1'},
#                                                      2: {'principal': 'principal_2',
#                                                      'operation': 'operation_2',
#                                                      'permissionType': 'permissionType_2'}}}

def parse_file(filename, principal, desired_resource_name):
    resources_dict = {}
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            # Get resourceType and name from ACL header
            # match part after 'name=' before comma
            # match part after 'resourceType=' before comma
            if line.startswith('Current ACLs'):
                resource_name = re.findall('name=(.*?),', line)[0]
                resource_type = re.findall('resourceType=(.*?),', line)[0]
            # When desired_resource_name is defined - find certain resource for name
            if desired_resource_name:
                # Compare desired name with current from line
                if desired_resource_name == resource_name and (resource_name, resource_type) not in resources_dict:
                    # create a new dictionary if matched, and it does not exist
                    # {'resource_name_1': {'name': 'resource_name_1', 'type': 'TOPIC'}}
                    resources_dict[(resource_name, resource_type)] = {'name': resource_name, 'type': resource_type}
                if desired_resource_name != resource_name:
                    continue
            # When desired_resource_name not defined create dictionaries for each resource
            elif (resource_name, resource_type) not in resources_dict:
                resources_dict[(resource_name, resource_type)] = {'name': resource_name, 'type': resource_type}

            # Get desired principal from rule string
            if line.startswith('(principal=User'):
                # match part after 'User:' before comma
                principal_match = re.findall(f'User:({principal}),', line)
                # If match principal - get operation and permissionType from line
                # match part after 'operation=' before comma
                # match part after 'permissionType=' before comma
                # and put into dictionary
                if len(principal_match) != 0:
                    operation_match = re.findall('operation=(.*?),', line)[0]
                    permission_type = re.findall('permissionType=(.*?)\)', line)[0]
                    resources_dict[(resource_name, resource_type)][
                        len(resources_dict[(resource_name, resource_type)]) - 1] = {
                        'principal': principal_match[0],
                        'operation': operation_match,
                        'permissionType': permission_type}

    acl_dict = delete_empty_acls(resources_dict)
    return acl_dict


# Delete dictionaries without the desired principal
# find dictionaries without ACL: # {('resource_name_1','resource_type_1'): {'name': 'resource_name_1', 'type': 'TOPIC'}}
# when desired principal does not have operations for this resource
def delete_empty_acls(resources_dict):
    acl_dict = resources_dict
    resources_to_del = []
    # Find dictionaries with length == 2 - only 'name' and 'type' values inside
    for resource in acl_dict:
        if len(acl_dict[resource]) == 2:
            resources_to_del.append(resource)
    for resource in resources_to_del:
        del (acl_dict[resource])
    return acl_dict


# Print all ACL from result dictionary
# for the desired principal and resourceType
def print_acls_pretty(acl_dict, desired_resource_type):
    for resource in acl_dict:
        # When find certain resource type
        # check desired_resource_type is defined
        if desired_resource_type:
            # compare 'type' value with desired resource_type
            if acl_dict[resource]["type"] == desired_resource_type:
                print(f'{acl_dict[resource]["type"]}: {acl_dict[resource]["name"]}')
                for acl_elm in acl_dict[resource]:
                    if acl_elm != 'name' and acl_elm != 'type':
                        print(f'{acl_elm}:\t{acl_dict[resource][acl_elm].get("principal")}:\t'
                              f'{acl_dict[resource][acl_elm].get("permissionType")}\t'
                              f'{acl_dict[resource][acl_elm].get("operation")}')
        else:
            print(f'{acl_dict[resource]["type"]}: {acl_dict[resource]["name"]}')
            for acl_elm in acl_dict[resource]:
                if acl_elm != 'name' and acl_elm != 'type':
                    print(f'{acl_elm}:\t{acl_dict[resource][acl_elm].get("principal")}:\t'
                          f'{acl_dict[resource][acl_elm].get("permissionType")}\t'
                          f'{acl_dict[resource][acl_elm].get("operation")}')


def print_acls(acl_dict, desired_resource_type):
    for resource in acl_dict:
        if desired_resource_type:
            if acl_dict[resource]["type"] == desired_resource_type:
                for acl_elm in acl_dict[resource]:
                    if acl_elm != 'name' and acl_elm != 'type':
                        print(f'{acl_dict[resource][acl_elm].get("principal")}:'
                              f'{acl_dict[resource][acl_elm].get("operation")}:'
                              f'{acl_dict[resource]["name"]}:')
        else:
            for acl_elm in acl_dict[resource]:
                if acl_elm != 'name' and acl_elm != 'type':
                    print(f'{acl_dict[resource][acl_elm].get("principal")}:'
                          f'{acl_dict[resource][acl_elm].get("operation")}:'
                          f'{acl_dict[resource]["name"]}:')


# Parse menu arguments for informational messages
if menu_args.list:
    print_resource_type_list()
if menu_args.usage:
    print_usage()
if not menu_args.list or not menu_args.usage:
    if not menu_args.file:
        menu_parser.error("-f/--file is required argument.")

result_dict = parse_file(menu_args.file, menu_args.principal, menu_args.name)

if menu_args.pretty:
    print_acls_pretty(result_dict, menu_args.type)
else:
    print_acls(result_dict, menu_args.type)
