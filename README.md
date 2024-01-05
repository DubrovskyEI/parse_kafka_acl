# parse_kafka_acl.py

### Description

This script allows you to obtain access rules from Kafka ACL list in required format

Rules may be filtered for next criteria:

1. Principal
2. Resource type
3. Resource name

### Execution

A file with a Kafka ACL list is passed to the input as a required parameter -f/--file

Examples of running the script (output when run with the --usage parameter)

#### 1. Get ACLs for each principal and resource in human readable format:

```CLI
python parse_kafka_acl.py --file sample_list.txt --pretty
```

#### 2. Get ACLs for all topics for user with CN "testuser":

```CLI
python parse_kafka_acl.py --file sample_list.txt --principal testuser --type topic
```

#### 3. Get ACLs for all groups:

```CLI
python parse_kafka_acl.py --file sample_list.txt --type group
```

#### 4. Get ACLs for topic with name "kafka-topic1":

```CLI
python parse_kafka_acl.py --file sample_list.txt --type topic --name kafka-topic1
```

#### 5. Get ACLs for resources with name "*":

```CLI
python parse_kafka_acl.py --file sample_list.txt --name *
```

### Operation logic

Access rules are stored in a dictionary:

```Text
acl_dict = {('resource_name_1','resource_type_1'): {'name': 'resource_name_1',
                                                    'type': 'TOPIC',
                                                    1: {'principal': 'principal_1', 'operation': 'operation_1', 'permissionType': 'permissionType_1'},
                                                    2: {'principal': 'principal_2', 'operation': 'operation_2', 'permissionType': 'permissionType_2'}}}
```

The key value for a resource that uniquely identifies it is a tuple of the form ('resource_name_1','resource_type_1')
Keys in the dictionary for each resource:

- **name** resource name
- **type** resource type
- **порядковый номер правила** the value is a dictionary with keys:
  - **principal** principal
  - **operation** operation
  - **permissionType** permission type								
 
The ACL file is read line by line, each line is parsed using regular expressions and the values are written to the dictionary.

###  Get the Kafka ACLs for all resources

```CLI
kafka-acls.sh --list --bootstrap-server localhost:9092 --command-config client.properties.example > sample_list.txt
```

### References

> References
> 1. https://docs.confluent.io/platform/current/kafka/authorization.html
> 2. https://kafka.apache.org/20/javadoc/org/apache/kafka/common/resource/ResourceType.html
> 3. https://pythonworld.ru/tipy-dannyx-v-python/slovari-dict-funkcii-i-metody-slovarej.html
> 4. https://jenyay.net/Programming/Argparse
> 5. https://pyneng.readthedocs.io/ru/latest/book/additional_info/argparse.html
> 6. https://www.instaclustr.com/support/documentation/kafka/accessing-and-using-kafka/kafka-acl-management/
