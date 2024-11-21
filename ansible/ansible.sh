#!/bin/bash
ansible-playbook -i ./hosts -i ./user -i ./fixed --connection=local $1