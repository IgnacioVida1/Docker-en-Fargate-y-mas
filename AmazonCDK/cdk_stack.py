from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_iam as iam,
)
from constructs import Construct

class StudentsApiStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        Vpc = ec2.Vpc.from_lookup(self, "MyVPC", vpc_id="vpc-0eb91d56cab4a9114")

        cluster = ecs.Cluster(self, "StudentsCluster", vpc=Vpc)

        task_definition = ecs.FargateTaskDefinition(
            self, "TaskDef",
            execution_role=iam.Role.from_role_arn(self, "LabRole",
                "arn:aws:iam::218543369212:role/LabRole",
                mutable=False),
            cpu=256,
            memory_limit_mib=512,
        )

        task_definition.add_container("StudentsContainer",
            image=ecs.ContainerImage.from_registry(
                "218543369212.dkr.ecr.us-east-1.amazonaws.com/api-students:latest"),
            port_mappings=[ecs.PortMapping(container_port=8000)]
        )
        Subnet = [ec2.Subnet.from_subnet_id(self, "Subnet1", "subnet-0cd04a0321ba04cb9")]
        ecs.FargateService(
            self, "FargateService",
            cluster=cluster,
            task_definition=task_definition,
            assign_public_ip=True,
            desired_count=1,
            vpc_subnets=ec2.SubnetSelection(subnets=Subnet)
        )
