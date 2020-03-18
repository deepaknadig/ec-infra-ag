#!/bin/bash

ssh ubuntu@10.10.10.11 "sync; sync; sudo /sbin/shutdown -h now"
ssh ubuntu@10.10.10.12 "sync; sync; sudo /sbin/shutdown -h now"
ssh ubuntu@10.10.10.13 "sync; sync; sudo /sbin/shutdown -h now"
ssh ubuntu@10.10.10.14 "sync; sync; sudo /sbin/shutdown -h now"

