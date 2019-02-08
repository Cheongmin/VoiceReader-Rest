resource "aws_instance" "master" {
  ami = "${var.ami}"
  instance_type = "${var.instance_type}"
  key_name = "${var.key_pair_name}"
  # user_data = "${file("${var.bootstrap_path}")}"
  vpc_security_group_ids = ["${aws_security_group.sgswarm.id}"]

  tags {
    Name  = "master"
  }

  connection {
    user = "${var.default_ec2_username}"
    type = "ssh"

    private_key = "${file(var.pri_key_path)}"
    timeout     = "2m"
  }

  provisioner "remote-exec" {
    inline = [
      "sudo yum update -y",
      "sudo yum install -y python",
      "sudo yum install ${var.docker_package_version} -y",
      "sudo service docker start",
      "sudo usermod -aG docker ${var.default_ec2_username}"
    ]
  }

  provisioner "local-exec" {
    command = <<EOF
      echo "[masters]" > inventory
      echo "${aws_instance.master.public_ip} ansible_ssh_user=${var.default_ec2_username} ansible_ssh_private_key_file=${var.pri_key_path}" >> inventory
      EOF
  }

  provisioner "local-exec" {
    command = <<EOF
      ANSIBLE_HOST_KEY_CHECKING=False \
      ansible-playbook -i inventory playbook.yml
      EOF
  }
}