# logs.tf

# Set up CloudWatch group and log stream and retain logs for 30 days
resource "aws_cloudwatch_log_group" "xai_log_group" {
  name              = "/ecs/xai-app"
  retention_in_days = 30

  tags = {
    Name = "xai-log-group"
  }
}

resource "aws_cloudwatch_log_stream" "xai_log_stream" {
  name           = "xai-log-stream"
  log_group_name = aws_cloudwatch_log_group.xai_log_group.name
}
