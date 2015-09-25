This file lists all event/trigger/notification this application can generate during running. Each of these take a category according to their importance and trigger value indicates what to do if this event occurs

Each event may be LOGGED at least.

Trigger significations :

  * NOTIFY => send message to system administrator, like by mail, or SMS, or other notification service

|            Name                | Category |  TRIGGER  |            Description          |
|--------------------------------|----------|-----------|-----------------|
| CERTIFICATE_CA_INVALID         | CRITICAL | NOTIFY    | the certificate authority has expired            |
| CERTIFICATE_CA_SOONEXPIRED     | WARNING  | NOTIFY    | the certificate authority will expire |
| CERTIFICATE_SERVER_INVALID     | CRITICAL | NOTIFY    | the server certificate is invalid (unusable)
| CERTIFICATE_SERVER_SOONEXPIRED | CRITICAL | NOTIFY    | the server certificate will expire soon
| DATABASE_UNREACHABLE           | CRITICAL | NOTIFY    | the database adapter is unable to open the remote database
| DATABASE_UPDATE_INAPPLICABLE   | CRITICAL | NOTIFY    | an update request must not be satisfy (too more retry)
| DATABASE_UPDATE_TOMOREQUEUED   | WARNING  | NOTIFY    | the update queue is too large
