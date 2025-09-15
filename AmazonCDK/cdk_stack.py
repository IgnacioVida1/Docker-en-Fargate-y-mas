from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_iam as iam,
)
from constructs import Construct

class ApiStudentsCdkStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        vpc_ = ec2.Vpc.from_vpc_attributes(
               self, "MyVPC",
               vpc_id="vpc-0eb91d56cab4a9114",
               availability_zones=["us-east-1a", "us-east-1b"],
               public_subnet_ids=["subnet-0cd04a0321ba04cb9", "subnet-06edefff6ec34b082"])

        cluster = ecs.Cluster(self, "StudentsCluster", vpc=vpc_)

        task_definition = ecs.FargateTaskDefinition(
            self, "TaskDef",
            execution_role=iam.Role.from_role_arn(self, "LabRole",
                "arn:aws:iam::218543369212:role/LabRole",
                mutable=False),
            task_role=iam.Role.from_role_arn(self, "LabTaskRole", 
                "arn:aws:iam::218543369212:role/LabRole", mutable=False),
            cpu=256,
            memory_limit_mib=512,
        )
        sg = ec2.SecurityGroup(
             self, "FargateSG",
             vpc=vpc_,
             description="Allow HTTP traffic on port 8000",
             allow_all_outbound=True,
        )

        sg.add_ingress_rule(
             peer=ec2.Peer.any_ipv4(),
             connection=ec2.Port.tcp(8000),
             description="Allow public access to port 8000"
        )

        task_definition.add_container("StudentsContainer",
            image=ecs.ContainerImage.from_registry(
                "218543369212.dkr.ecr.us-east-1.amazonaws.com/api-students:latest"),
            port_mappings=[ecs.PortMapping(container_port=8000)]
        )
        subnet1 = ec2.Subnet.from_subnet_id(self, "Subnet1", "subnet-0cd04a0321ba04cb9")
        subnet2 = ec2.Subnet.from_subnet_id(self, "Subnet2", "subnet-06edefff6ec34b082")
        ecs.FargateService(
            self, "FargateService",
            cluster=cluster,
            task_definition=task_definition,
            assign_public_ip=True,
            desired_count=1,
            vpc_subnets=ec2.SubnetSelection(subnets=[subnet1, subnet2]),
            security_groups=[sg]
        )
