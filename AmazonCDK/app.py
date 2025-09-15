import os

import aws_cdk as cdk

from api_students_cdk.api_students_cdk_stack import ApiStudentsCdkStack


app = cdk.App()
ApiStudentsCdkStack(app, "ApiStudentsCdkStack",env=cdk.Environment(account='218543369212', region='us-east-1'))

app.synth()
