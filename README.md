# Description

This role sets up 4 components:
- OpenKM
- xvfb
- jBMP Console
- Status Plugins

And it requires PostgreSQL

# Configuration

These settings are all mandatory:
```yaml
openkm_domain:               'openkm.example.org'
openkm_admin_password:       'changeIfYouCare'
openkm_installation_id:      '00000000-0000-0000-0000-000000000000'
openkm_docker_registry_user: 'some_user'
openkm_docker_registry_pass: 'some_password'
openkm_jbpm_db_pass:         'another_password'
openkm_jbpm_admin_password:  'one_more_password'
openkm_db_pass:              'yet_another_password'
openkm_mail_from:            'noreply@example.org'
openkm_mail_smtp_host:       'smtp.example.org'
openkm_mail_smtp_port:       587
openkm_mail_smtp_user:       'another_user'
openkm_mail_smtp_pass:       'password_too'
```

# Installation

Few things are manual:
1. Set migrations to create tables. This is only needed during the first run.
[jbpm-console.properties](./templates/config/jbpm-console.properties):
```
hibernate.hbm2ddl=create
```
[openkm.properties](./templates/config/openkm.properties):
```
spring.jpa.hibernate.ddl-auto=create-only
```
Running `create` again will break OpenKM. Be careful.
OpenKM will change it to `none` after running.
2. DB configuration will fail, because tables don't exist yet.
So you need to rerun the role after some time.
3. Installation ID is generated automatically on the first run,
it should be kept and shared with OpenKM support for licensing.
If you already have a key, it will be overwritten by OpenKM, so role needs to run again.
4. Change jBPM console admin password manually.

# Upgrade

This role has 3 components, which could be upgraded - openkm, jbmp-console and status plugins:
```
openkm_version:                 '8.1.7'
openkm_jbpm_version:            '2.1'
openkm_jbpm_checksum:           'sha256:100a52e4ac4892c35fbaaab10245c02396e155f2078dd1471c89fc590455b19b'
openkm_status_plugins_url:      'https://status-misc.ams3.digitaloceanspaces.com/openkm/statusPlugins.jar'
openkm_status_plugins_checksum: 'e2e79e6320683af4b47172e03dfa056423c413c35e3bafb03e19aa99774290ef'
```

Read carefully the Changelog and Migration Guide, as they might have manual steps.
During the jBPM Console upgrade - set `hibernate.hbm2ddl=update`.

# Management

The container is managed using Docker Compose.
```
❯ dc ps
NAME          IMAGE                                                   COMMAND                  SERVICE   CREATED      STATUS                 PORTS
openkm-app    docker.openkm.com/private/professional:8.1.11-nonroot   "/opt/tomcat/bin/cat…"   app       4 days ago   Up 5 hours (healthy)
openkm-xvfb   docker.openkm.com/private/professional:8.1.11-nonroot   "/usr/bin/Xvfb :1"       xvfb      4 days ago   Up 5 hours (healthy)   8080/tcp
```

# Useful links:
- [OpenKM Support](https://support.openkm.com)
- [OpenKM Documentation](https://docs.openkm.com/kcenter/view/okm-8.1/)
- [OpenKM Changelog](https://docs.openkm.com/kcenter/view/okm-8.1/changelog.html)
- [jBPM Console Documentation](https://docs.openkm.com/kcenter/view/jbpm-console-2x/)
- [jBPM Console Migration Guide](https://docs.openkm.com/kcenter/view/jbpm-console-2x/migration-guide.html)
- [hibernate.hbm2ddl.auto](https://docs.jboss.org/hibernate/orm/6.4/javadocs/org/hibernate/cfg/SchemaToolingSettings.html#HBM2DDL_AUTO)
- [spring.jpa.hibernate.ddl-auto](https://docs.spring.io/spring-boot/how-to/data-initialization.html)
