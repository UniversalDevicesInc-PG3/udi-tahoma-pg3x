# Somfy API Endpoints

<!-- markdownlint-disable MD022 MD013 -->

This document lists the API endpoints for the Somfy-based Phantom Blinds
system.

## Base URL Pattern

```text
http://{gateway_ip}/
```text

## Gateway Endpoints

### Get Gateway Information

```text
GET /gateway
```text

Returns basic gateway information and capabilities.

### Get Home Configuration

```text
GET /home
```text

Returns complete home configuration including rooms, shades, and scenes.

## Room Endpoints

### List All Rooms

```text
GET /home/rooms
```text

### Get Room Details

```text
GET /home/rooms/{room_id}
```text

## Shade Endpoints

### Get Shade Details

```text
GET /home/shades/{shade_id}
```text

### Move Shade

```text
PUT /home/shades/{shade_id}/motion
```text

**Request Body:**

```json
{
  "positions": {
    "primary": 0-100,
    "secondary": 0-100,
    "tilt": 0-100,
    "velocity": 0-100
  }
}
```text

### Get Shade Positions

```text
GET /home/shades/positions?ids={shade_id}
```text

### Stop Shade

```text
PUT /home/shades/stop?ids={shade_id}
```text

## Scene Endpoints

### Get Scene Details

```text
GET /home/scenes/{scene_id}
```text

### Activate Scene

```text
PUT /home/scenes/{scene_id}/activate
```text

### Get Active Scenes

```text
GET /home/scenes/active
```text

### Scene Events (SSE)

```text
GET /home/scenes/events
```text

Server-Sent Events endpoint for scene updates.

## Event Endpoints

### Home Events (SSE)

```text
GET /home/events?sse=false&raw=true
```text

Main event stream for all home updates.

### Shade Events (SSE)

```text
GET /home/shades/events
```text

Server-Sent Events endpoint for shade status updates.

## Response Codes

- `200 OK` - Request successful
- `400 Bad Request` - Invalid request or not primary gateway
- `404 Not Found` - Resource not found
- `503 Service Unavailable` - Gateway setup not complete

## Authentication

**TODO**: Document authentication requirements for Somfy API

- API keys (if required)
- OAuth (if used)
- Basic auth (if used)

## Rate Limiting

**TODO**: Document any rate limiting policies

## Notes

- Most endpoints accept and return `application/json`
- SSE endpoints stream text/event-stream
- Position values are typically 0-100 (percentage)
- The gateway parameter can be an IP address or hostname (e.g., "gateway-2001-1234-5678.local")
