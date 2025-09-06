"""An AWS Python Pulumi program"""

import pulumi
import pulumi_aws as aws

default_vpc = aws.ec2.get_vpc(default=True)
subnets = aws.ec2.get_subnets(filters=[{"name": "vpc-id", "values": [default_vpc.id]}])

sg = aws.ec2.SecurityGroup("api-students-sg",
    description="Permitir entrada en puerto 8000",
    vpc_id=default_vpc.id,
    ingress=[{
        "protocol": "tcp",
        "from_port": 8000,
        "to_port": 8000,
        "cidr_blocks": ["0.0.0.0/0"]
    }],
    egress=[{
        "protocol": "-1",
        "from_port": 0,
        "to_port": 0,
        "cidr_blocks": ["0.0.0.0/0"]
    }]
)

cluster = aws.ecs.Cluster("api-students-cluster")

task_definition = aws.ecs.TaskDefinition("api-students-task",
    family="api-students-task",
    cpu="256",
    memory="512",
    network_mode="awsvpc",
    requires_compatibilities=["FARGATE"],
    execution_role_arn="arn:aws:iam::218543369212:role/LabRole",
    container_definitions=pulumi.Output.all().apply(
        lambda _: f"""
        [
            {{
                "name": "api-students",
                "image": "218543369212.dkr.ecr.us-east-1.amazonaws.com/api-students:latest",
                "portMappings": [{{ "containerPort": 8000, "hostPort": 8000 }}],
                "essential": true
            }}
        ]
        """
    )
)

service = aws.ecs.Service("api-students-service",
    cluster=cluster.arn,
    task_definition=task_definition.arn,
    desired_count=1,
    launch_type="FARGATE",
    network_configuration={
        "assign_public_ip": True,
        "subnets": subnets.ids,
        "security_groups": [sg.id],
    },
    opts=pulumi.ResourceOptions(depends_on=[task_definition])
)

pulumi.export("cluster_name", cluster.name)
