# UnfoTour Pin APIs with Social Posts Integration

## Overview

This project provides REST APIs for tourism pins with integrated social media posts. When users click on pins in the frontend, they can see detailed information including related social media content.

## API Endpoints

### 1. Get All Pins
```
GET /api/all/
```

Returns all published pins from all categories with basic information for map display.

**Query Parameters:**
- `search` (optional): Filter pins by name

**Response:**
```json
{
  "pins": [
    {
      "id": 1,
      "name": "Red Fort",
      "type": "mainattraction",
      "city_name": "Delhi",
      "latitude": 28.6562,
      "longitude": 77.2410,
      "description": "Historic fort in Delhi",
      "header_image": "https://example.com/image.jpg",
      "icon": "fort-icon",
      "rating": "4.50",
      "link": "https://example.com",
      "tags": ["historic", "monument"]
    }
  ],
  "total_count": 150
}
```

### 2. Get Pins by Type
```
GET /api/pins/<table_name>/
```

Returns pins from a specific category.

**Available table names:**
- `main-attractions`
- `things-to-do`
- `places-to-visit`
- `places-to-eat`
- `markets`
- `country-info`
- `destination-guides`
- `place-information`
- `travel-hacks`
- `festivals`
- `famous-photo-points`
- `activities`
- `hotels`

**Response:**
```json
{
  "pins": [...],
  "total_count": 25,
  "table_name": "main-attractions"
}
```

### 3. Get Pin Details (Enhanced with Social Posts)
```
GET /api/pin/<slug>/
```

Returns detailed information about a specific pin including social media posts.

**Example slug:** `main-attractions-red-fort-a1b2c`

**Response:**
```json
{
  "pin": {
    "id": 1,
    "name": "Red Fort",
    "type": "mainattraction",
    "city_name": "Delhi",
    "latitude": 28.6562,
    "longitude": 77.2410,
    "description": "Historic fort in Delhi...",
    "header_image": "https://example.com/image.jpg",
    "icon": "fort-icon",
    "marker_icon": "fort-marker",
    "rating": "4.50",
    "link": "https://example.com",
    "tags": ["historic", "monument"],
    "slug": "main-attractions-red-fort-a1b2c",
    "created_by_name": "admin",
    "social_posts": [
      {
        "id": 1,
        "name": "Amazing Red Fort Visit",
        "platform": {
          "id": 1,
          "name": "YouTube",
          "code": "YT",
          "website": "https://youtube.com"
        },
        "link": "https://youtube.com/watch?v=xyz",
        "description": "Great video about Red Fort history",
        "tags": ["travel", "history"],
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
      }
    ]
  },
  "type": "main-attractions"
}
```

### 4. Get Social Posts for a Pin
```
GET /api/pin/<slug>/social-posts/
```

Returns only the social media posts for a specific pin.

**Response:**
```json
{
  "pin_slug": "main-attractions-red-fort-a1b2c",
  "pin_name": "Red Fort",
  "social_posts": [
    {
      "id": 1,
      "name": "Amazing Red Fort Visit",
      "platform": {
        "id": 1,
        "name": "YouTube",
        "code": "YT",
        "website": "https://youtube.com"
      },
      "link": "https://youtube.com/watch?v=xyz",
      "description": "Great video about Red Fort history",
      "tags": ["travel", "history"],
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total_posts": 1
}
```

## Frontend Integration

### For Map Display
Use `/api/all/` to get basic pin information for map markers.

### For Pin Click Details
When a user clicks on a pin:
1. Use the pin's `slug` from the map data
2. Call `/api/pin/<slug>/` to get detailed information with social posts
3. Display pin details and social media content

### Example Frontend Usage

```javascript
// Get all pins for map
fetch('/api/all/')
  .then(response => response.json())
  .then(data => {
    // Display pins on map
    data.pins.forEach(pin => {
      addMarkerToMap(pin);
    });
  });

// When user clicks a pin
function onPinClick(pinSlug) {
  fetch(`/api/pin/${pinSlug}/`)
    .then(response => response.json())
    .then(data => {
      // Show pin details modal/sidebar
      showPinDetails(data.pin);
      
      // Display social posts
      displaySocialPosts(data.pin.social_posts);
    });
}
```

## Database Models

### Pin Models
All pin models share common fields:
- `name`: Pin name
- `city`: Foreign key to City
- `pin`: Geographic point (latitude/longitude)
- `slug`: URL-friendly identifier
- `description`: Detailed description
- `header_image`: Main image URL
- `icon`: Icon identifier
- `marker_icon`: Map marker icon
- `tags`: Taggable tags
- `published`: Publication status
- `rating`: Rating out of 5
- `link`: External link

### Social Post Model
- `name`: Post title
- `platform`: Social media platform (YouTube, Instagram, etc.)
- `link`: URL to the post
- `description`: Post description
- `tags`: Taggable tags
- `published`: Publication status
- Links to various pin models

## Testing

Run the test script to verify API functionality:

```bash
python test_apis.py
```

## Development Notes

1. **Slug Format**: Slugs are auto-generated as `{model-type}-{name-slug}-{random-suffix}`
2. **Social Posts**: Linked to pins via foreign keys in the SocialPost model
3. **Performance**: Queries use `select_related` and `prefetch_related` for optimization
4. **Filtering**: Only published pins and posts are returned in API responses

## Error Handling

- **404**: Pin not found or not published
- **400**: Invalid table name or slug format
- **500**: Server error

All endpoints return appropriate HTTP status codes and error messages.