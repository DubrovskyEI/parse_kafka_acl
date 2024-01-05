# parse_kafka_acl.py

### Описание

Данный скрипт позволяет получить правила доступа из выгрузки ACL Kafka в удобном формате

Возможна фильтрация правил по следующим признакам:

1. Принцпипал
2. Тип ресурса
3. Имя ресурса

### Запуск

На вход в качестве обязательного параметра -f/--file передается файл со списком ACL Kafka

Примеры запуска скрипта (вывод при запуске с параметром --usage)

#### 1. Вывести в консоль все ACL для каждого приницпала и ресурса в удобочитаемом формате:

```CLI
python parse_kafka_acl.py --file sample_list.txt --pretty
```

#### 2. Вывести в консоль все ACL для пользователя с CN "testuser" для ресурсов с типом "TOPIC":

```CLI
python parse_kafka_acl.py --file sample_list.txt --principal testuser --type topic
```

#### 3. Вывести в консоль все ACL для ресурсов с типом "GROUP":

```CLI
python parse_kafka_acl.py --file sample_list.txt --type group
```

#### 4. Вывести в консоль все ACL для топика с именем "kafka-topic1":

```CLI
python parse_kafka_acl.py --file sample_list.txt --type topic --name kafka-topic1
```

#### 5. Вывести в консоль все ACL для ресурсов c именем "*":

```CLI
python parse_kafka_acl.py --file sample_list.txt --name *
```

### Логика работы

Правила доступа хранятся в словаре вида:

```Text
acl_dict = {('resource_name_1','resource_type_1'): {'name': 'resource_name_1',
                                                    'type': 'TOPIC',
                                                    1: {'principal': 'principal_1', 'operation': 'operation_1', 'permissionType': 'permissionType_1'},
                                                    2: {'principal': 'principal_2', 'operation': 'operation_2', 'permissionType': 'permissionType_2'}}}		
```
		
Ключевое значение для ресурса, которое его однозначно идентифицирует - кортеж вида ('resource_name_1','resource_type_1')
Ключи в словаре для каждого ресурса:

- **name** имя ресурса
- **type** тип ресурса
- **порядковый номер правила** значением является словарь с ключами:
  - **principal** принципал
  - **operation** операция
  - **permissionType** тип разрешения
  
Файл с ACL читается построчно, каждая строка разбирается с применением регулярных выражений и значения записываются в словарь.

### Получение выгрузки ACL из Kafka для всех ресурсов

```CLI
kafka-acls.sh --list --bootstrap-server localhost:9092 --command-config client.properties.example > sample_list.txt
```

### References

> References
> 1. https://docs.confluent.io/platform/current/kafka/authorization.html
> 2. https://kafka.apache.org/20/javadoc/org/apache/kafka/common/resource/ResourceType.html
> 3. https://pythonworld.ru/tipy-dannyx-v-python/slovari-dict-funkcii-i-metody-slovarej.html
> 4. https://jenyay.net/Programming/Argparse
> 5. https://pyneng.readthedocs.io/ru/latest/
> 6. https://www.instaclustr.com/support/documentation/kafka/accessing-and-using-kafka/kafka-acl-management/
