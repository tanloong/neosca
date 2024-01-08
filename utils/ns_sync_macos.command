#!zsh
# On the first time running this script:
#   1. Config port forwarding between host and guest
#   2. ssh-genkey
#   3. ssh-copy-id
#   4. vi ~/.ssh/config and add lines below
#     """Host=host
#       Hostname=[host ip address]
#       User [host username]
#     """


rsync -av -e ssh --exclude '*ns_data*' --exclude '__pycache__' --exclude '.*' --exclude 'build' --exclude 'dist' --exclude 'corpus' --exclude '*egg-info' host:/home/tan/projects/neosca ~/Desktop/

mkdir -p ~/Desktop/neosca/src/neosca/ns_data
sshfs -o follow_symlinks host:/home/tan/projects/neosca/src/neosca/ns_data ~/Desktop/neosca/src/neosca/ns_data
