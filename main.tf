provider "aws" {
  region = "us-east-1"
}

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

resource "aws_security_group" "fargate_sg" {
  name        = "terraform-sg"
  description = "Permitir trafico en puerto 8000"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_ecs_cluster" "students_cluster" {
  name = "api-students-cluster"
}

resource "aws_ecs_task_definition" "students_task" {
  family                   = "api-students-task"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = "arn:aws:iam::218543369212:role/LabRole"

  container_definitions = jsonencode([{
    name      = "students-api"
    image     = "218543369212.dkr.ecr.us-east-1.amazonaws.com/api-students:latest"
    essential = true
    portMappings = [{
      containerPort = 8000
      hostPort      = 8000
      protocol      = "tcp"
    }]
  }])
}

resource "aws_ecs_service" "students_service" {
  name            = "students-service"
  cluster         = aws_ecs_cluster.students_cluster.id
  task_definition = aws_ecs_task_definition.students_task.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = data.aws_subnets.default.ids
    assign_public_ip = true
    security_groups  = [aws_security_group.fargate_sg.id]
  }

  depends_on = [aws_ecs_cluster.students_cluster]
}
