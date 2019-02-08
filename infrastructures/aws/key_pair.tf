resource "aws_key_pair" "ec2-key" {
  key_name   = "${var.key_pair_name}"
  public_key = "${file(var.pub_key_path)}"
}
