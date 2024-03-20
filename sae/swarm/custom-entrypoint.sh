set -eo pipefail
command1="--bind-address=0.0.0.0"
command2="--init-file /docker-entrypoint-initdb.d/init.sql"
/docker-entrypoint.sh mysqld $command1 $command2
