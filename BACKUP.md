# Backups

There's two folders that need to be backed up:

* `/data/openkm/backup` - PostgreSQL [database dump](https://www.postgresql.org/docs/13/app-pgdump.html)
* `/data/openkm/app/repo` - Uploaded files.

The database dumps are done with a [systemd timer](https://www.freedesktop.org/software/systemd/man/systemd.timer.html) and then backed up with [Restic](https://github.com/status-im/infra-role-restic-backups), as are the `data` folders:

```text
$ s list-timers -a | grep dump-openkm-db
Fri 2025-09-19 00:00:00 UTC 12h left     Thu 2025-09-18 00:00:01 UTC 11h ago      dump-openkm-db.timer         dump-openkm-db.service
```

# Restoring

## Backup Existing Data

Create a copy of OpenKM folder

```bash
cd /docker/openkm
docker compose -f docker-compose.db.yml -f docker-compose.oauth.yml -f docker-compose.yml down
cd ../
sudo cp -a openkm openkm_bkp
```

## Restore Backup

To restore backup to the same directory the destination permissions need to be changed:

```bash
sudo chmod g+w -R /docker/openkm/{backup,app/repo}

sudo -i -u restic restic restore --target=/ 12345678 # okmrepo
sudo -i -u restic restic restore --target=/ 87654321 # pgdumpdir

sudo chown -R openkm:openkm /docker/openkm/app/repo
sudo chown openkm:docker /docker/openkm/app/repo /docker/openkm/app/repo/.system.key
sudo chown -R dockremap:dockremap /docker/openkm/backup
sudo chown dockremap:docker /docker/openkm/backup

sudo chmod g-w -R /docker/openkm/{backup,app/repo}
```

```text
Summary: Restored 6 files/dirs (0 B) in 0:00, skipped 174 files/dirs 1.813 MiB
```

By using `--target=/` we restore the backup to the same location from which it was copied.

## Load Database Dump

:warning: This is a destructive operation, especially when done using an older backup.

Purge the DB to make sure restore really works:

```bash
sudo rm -fr /docker/openkm/data/pgdata
docker compose -f docker-compose.db.yml up -d
```

Restore the databases:

```bash
docker exec -i openkm-db \
    pg_restore \
      -p 5432 \
      -U postgres \
      -d "jbpm_console" \
      "/backup/jbpm_console"
docker exec -i openkm-db \
    pg_restore \
      -p 5432 \
      -U postgres \
      -d "openkm" \
      "/backup/openkm"
```

Other containers needs to be restarted afterewards:

```bash
docker compose -f docker-compose.yml -f docker-compose.oauth.yml -f docker-compose.db.yml up -d
```
