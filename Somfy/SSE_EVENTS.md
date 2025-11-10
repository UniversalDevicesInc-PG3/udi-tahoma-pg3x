# Server-Sent Events (SSE)

<!-- markdownlint-disable MD022 MD013 -->

This document describes the SSE event system used by the Somfy/Phantom Blinds
gateway.

## Overview

The gateway uses Server-Sent Events (SSE) to push real-time updates to clients. This allows the plugin to receive immediate notifications when shades move, scenes activate, or configuration changes occur.

## Event Stream Endpoint

```text
GET /home/events?sse=false&raw=true
```text

## Connection Details

- **Content-Type**: `text/event-stream`
- **Connection**: Keep-alive
- **Heartbeat**: "100 HELO" message sent periodically

## Event Format

Events are sent as newline-delimited JSON objects:

```json
{
  "evt": "event-type",
  "id": 12345,
  "isoDate": "2025-11-07T19:55:10.531Z",
  ...additional fields...
}
```text

## Event Types

### homedoc-updated

Indicates that the home configuration has been updated.

```json
{
  "evt": "homedoc-updated",
  "isoDate": "2025-11-07T19:55:10.531Z"
}
```text

**Action**: Re-fetch home configuration

### scene-add

A new scene has been added or an existing scene has been redefined.

```json
{
  "evt": "scene-add",
  "id": 12345,
  "isoDate": "2025-11-07T19:55:10.531Z"
}
```text

**Action**:

- Check if scene already exists
- If new, trigger discovery to create node
- If existing, update configuration

### shade-position

Shade position has changed.

```json
{
  "evt": "shade-position",
  "id": 67890,
  "positions": {
    "primary": 50,
    "secondary": 0,
    "tilt": 0,
    "velocity": 100
  },
  "isoDate": "2025-11-07T19:55:10.531Z"
}
```text

### scene-activated

A scene has been activated.

```json
{
  "evt": "scene-activated",
  "id": 12345,
  "isoDate": "2025-11-07T19:55:10.531Z"
}
```text

### scene-deactivated

A scene has been deactivated.

```json
{
  "evt": "scene-deactivated",
  "id": 12345,
  "isoDate": "2025-11-07T19:55:10.531Z"
}
```text

## Heartbeat

The gateway sends periodic heartbeat messages:

```text
100 HELO
```text

These are not JSON and should be handled separately to confirm the connection is alive.

## Error Handling

### Connection Errors

The plugin implements retry logic with exponential backoff:

- Max retries: 5
- Base delay: 1 second
- Delay formula: `base_delay * (2 ** retries)`

### Not Found Response

If the endpoint returns:

```json
{
  "message": "Not Found"
}
```text

**Action**: Restart the SSE client connection

## Implementation Notes

### Threading

- SSE client runs in an async thread
- Events are queued for processing by the main event loop
- Thread-safe queue with condition variables for synchronization

### Event Processing

- Events are processed in `isoDate` order (oldest first)
- Events older than 2 minutes are automatically removed
- "home" events (without isoDate) are processed separately

### Connection Management

```python
async with aiohttp.ClientSession() as session:
    async with session.get(url) as response:
        async for val in response.content:
            line = val.decode().strip()
            if not line:
                continue
            # Process line...
```text

## Example Event Sequence

1. Client connects to SSE endpoint
2. Gateway sends "100 HELO" heartbeat
3. User activates scene in app
4. Gateway sends `scene-activated` event
5. Gateway sends `shade-position` events for affected shades
6. Plugin processes events and updates node states
7. Periodic "100 HELO" heartbeats maintain connection

## Testing SSE Connection

You can test the SSE connection using curl:

```bash
curl -N -H "Accept: text/event-stream" "http://{gateway_ip}/home/events?sse=false&raw=true"
```text

This will show the raw event stream from the gateway.
