import aws_cdk as core
import aws_cdk.assertions as assertions

from michael_jin_shun_leong_question_1.michael_jin_shun_leong_question_1_stack import MichaelJinShunLeongQuestion1Stack

# example tests. To run these tests, uncomment this file along with the example
# resource in michael_jin_shun_leong_question_1/michael_jin_shun_leong_question_1_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = MichaelJinShunLeongQuestion1Stack(app, "michael-jin-shun-leong-question-1")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
