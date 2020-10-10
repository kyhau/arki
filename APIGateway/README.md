# API Gateway

1. API Gateway vs. ALB (https://dashbird.io/blog/aws-api-gateway-vs-application-load-balancer/)

1. Be careful with AWS Private API Gateway Endpoints ([Ref](https://st-g.de/2019/07/be-careful-with-aws-private-api-gateway-endpoints))
    - The setting **Enable Private DNS Name**,  will prevent all access to any regional/public API Gateway in the whole AWS region!
    - Solution 1:
        - Disable the private DNS name, and
        - Set one of following HTTP headers:
            - `Host: <api-id>.execute-api.<region>.amazonaws.com`, or
            - `x-apigw-api-id: <api-id>`
    - Solution 2:
        - Not require to set custom headers with disabled DNS resolution
        - Use a custom domain name configured in the API Gateway and an ALB in front of it.
        - Based on an IP target group, the ALB would forwards the requests to the ENIs of the VPC Endpoint.

1. Connecting API Gateway and private ALB ([stackoverflow](https://stackoverflow.com/questions/50782573/connecting-aws-api-gateway-and-private-alb)])

    2. For a REST API, you can create a VPC link to an NLB. The NLB and API must be owned by the same AWS account ([Ref](https://docs.aws.amazon.com/apigateway/latest/developerguide/getting-started-with-private-integration.html)).
        - You can create a VPC link to an NLB, but not an ALB (that's the invalid endpoint address issue you've been seeing)

    1. For a HTTP API, you can create a VPC link to an ALB, NLB, or resources registered with an AWS Cloud Map service. However, all resources must be owned by the same AWS account (including the load balancer or AWS Cloud Map service, VPC link and HTTP API)
    ([Ref](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-develop-integrations-private.html)).
        - https://aws.amazon.com/about-aws/whats-new/2020/03/api-gateway-private-integrations-aws-elb-cloudmap-http-apis-release/
        - https://aws.amazon.com/blogs/compute/building-better-apis-http-apis-now-generally-available/


1. Using static IP addresses for ALB (NLB -> ALB) https://aws.amazon.com/blogs/networking-and-content-delivery/using-static-ip-addresses-for-application-load-balancers/

1. API Gateway for multi account architecture https://www.levvel.io/resource-library/aws-api-gateway-for-multi-account-architecture
