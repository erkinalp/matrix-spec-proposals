# MSC3926: FIFOs and notification queues as rooms

This proposal seeks to introduce queues as rooms. 

## The basics

This proposal proposes two new room versions, one of which being single writer, many reader;
the other being single reader, many writer. Those two paradigms have a significance
in many communication concepts. Unlike existing room versions, those will not require any conflict
resolution in their authorisation rules, as a single writer room can be made conflict-free by virtue
of making the point of view of the single writer canonical, and same applies to the single reader's
point of view in case of a single reader room.

Those two paradigms have real world use cases. Single writer one can be used as an announcement feed,
and similarly, the single reader one can be used as a notification queue. In fact, I am also proposing
to replace the current notification system by one based on single reader, many writer queues
described in this very proposal.

#### Permissions event

The creator of the room will be the only allowed writer in case of the single writer variant. Similarly,
the creator of the room will be the only allowed reader in case of the single reader variant. Creators
of this room versions will always have read-write access to these two types of rooms. Room creators will
be the only users that are allowed to modify permissions of this type of rooms. In case of single
writer rooms, the creator will set who can read which types of events; and in case of single reader rooms,
the creator will set who can send which types of events. Power levels shall not apply to those two room
versions. Instead, a whitelist approach shall be used. The following exemplifies what a permissions
event shall look like:

```json
{
  "type": "m.permissions",
  "content": {
      "permissions":
          {
             "m.room.*": ["@root:example.com", "@user:example.com"],
             "m.message": ["@user:example.com"]
          }  
  }
```

Each entry in the `permissions` property in the `m.permissions` event denotes the allowed senders/readers
for a certain event type given. The value is a list of users. Both the event type and the user target list
are globbable, subject to [GLOB](linkme:0.0.0.0) specification. This `m.permissions` event is only allowed
to be sent by the room creator.

The creator of the room will be the only allowed writer in case of the single writer variant. Similarly,
the creator of the room will be the only allowed reader in case of the single reader variant. Creators
of this room versions will always have read-write access to these two types of rooms. Room creators will
be the only users that are allowed to modify permissions of this type of rooms. In case of single
writer rooms, the creator will set who can read which types of events; and in case of single reader rooms,
the creator will set who can send which types of events.

### Room versions

The room version value for this room is `m.feed` for the single writer variant, and `m.queue` for
the single reader variant. Neither of those are "next" room versions, those are simply different versions
from usual truly multi user rooms.

`m.queue`, the single reader room version, shall be structured as a linear chain of permissions events
(in case of incomplete permissions events, the entry in the latest permissions event wins) and a bunch
of semi-ephemeral events that reference a permissions event in the room as their authorising event.
Semi-ephemeral data units shall otherwise be treated identically to persistent data units except that
they may be dropped server-side.

`m.feed`, the single writer room version, shall be structured as a linear chain of permissions events
(in case of incomplete permissions events, the entry in the latest permissions event wins) and a bunch
of persistent events that reference a permissions event in the room as their authorising event.

## Notification queues as rooms

Notification queues shall be the rooms of an acceptable notification queue room version. For the purposes
of this proposal, the only acceptable room version of a user's incoming notifications queue is `m.queue`.
Each user's notification queue shall use that user's MXID as its room ID (like `@zumbeispiel:example.com`).
Each user's notification queue shall be autocreated upon registration, however the user can create another
one by sending a new room create event at the same room ID. Recreation of a new notification queue under
the same identifier shall invalidate the events sent to the previous one as if they were not sent
in the first place. Permission failures that arise out of notification queues shall be reported
as success unless the sender of the event is the creator of the room. This is to prevent social engineering
attacks to work around personal mutes, as mutes in this notification system are based on lack of write
permission to the queue. In this room version, clients are not allowed to fetch individual events. They
are only allowed to either fetch all events, or fetch events received after the last read receipt. This 
allows an experience similar to how notifications are handled in YouTube.

### Notification event structure

## Authorisation rules applied to these room versions

### Single writer, many reader

TODO

### Single reader, many writer

TODO

## Potential issues

Mixed use of persistent and semi-ephemeral data units might cause issues in data unit handling
in certain server implementations. Certain users may get over-pinged, as this feature allows
sender-controlled mentions.

## Alternatives

Single writer rooms could also be created as regular rooms with power levels. No replacement for
the single reader variant.

## Security considerations

Denial of service possible in the single reader variant. No known isssues in the single writer variant.

## Unstable prefix

`org.matrix.msc.queue` can be used instead of `m.queue`, and `org.matrix.msc.feed` instead of `m.feed`.

## Dependencies

no known
