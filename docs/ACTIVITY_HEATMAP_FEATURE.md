# Portfolio Activity Heatmap Feature

## Overview

The Portfolio Activity Heatmap is a visual representation of project activity across all projects in a user's portfolio. It displays daily activity counts in a calendar-style heatmap, similar to GitHub's contribution graph, providing users with an at-a-glance view of their productivity and project engagement over time.

## Features

- **Calendar-style visualization**: Shows activity intensity for each day using color coding
- **Hover tooltips**: Displays detailed activity information for each day
- **Project breakdown**: Shows which projects contributed to each day's activity
- **Activity metrics**: Displays total activity, max/min daily activity, and total days active
- **Date range display**: Shows the earliest and latest activity dates
- **Responsive design**: Works on all screen sizes with Tailwind CSS styling

## How It Works

### Activity Sources

The heatmap aggregates activity from two main sources:

1. **File Uploads** (`ProjectFile.created_at`): Each file added to a project counts as one activity
2. **Project Creation** (`Project.created_at`): Each new project created counts as one activity

### Color Coding

The heatmap uses a blue color gradient to indicate activity intensity:

- **Gray** (`bg-slate-700`): No activity (0)
- **Dark Blue** (`bg-blue-900`): Very Low (1)
- **Blue** (`bg-blue-700`): Low (2-3)
- **Bright Blue** (`bg-blue-500`): Medium (4-7)
- **Light Blue** (`bg-blue-400`): High (8-14)
- **Lightest Blue** (`bg-blue-300`): Very High (15+)

## Architecture

### Backend Implementation

#### API Endpoint

```
GET /api/portfolio/<portfolio_id>/activity-heatmap/
```

**Response Format:**
```json
{
  "portfolio_id": 1,
  "total_activity": 245,
  "date_range": {
    "start": "2024-01-15",
    "end": "2025-03-14"
  },
  "activity_data": [
    {
      "date": "2024-01-15",
      "count": 3,
      "projects": [
        {"name": "Project A", "count": 2},
        {"name": "Project B", "count": 1}
      ]
    },
    ...
  ],
  "max_activity": 42,
  "min_activity": 1
}
```

#### View Class: `PortfolioActivityHeatmapView`

**Location**: `src/backend/app/views/portfolio_views.py`

**Key Features**:
- Permissions: `AllowAny` (respects portfolio privacy)
- Gets all projects in a portfolio
- Aggregates file and project creation activity by date
- Fills gaps in the date range with zero-activity entries
- Returns data sorted by date

**Implementation Details**:
- Uses Django's `TruncDate` function to group by date
- Uses `defaultdict` to efficiently aggregate activity
- Generates complete date range (no gaps) for visualization

### Frontend Implementation

#### Component: `PortfolioActivityHeatmap`

**Location**: `src/frontend/src/components/PortfolioActivityHeatmap.js`

**Key Features**:
- React functional component with hooks
- Fetches data from backend API
- Generates calendar weeks dynamically
- Displays color-coded activity cells
- Shows tooltips with detailed activity information
- Responsive design using Tailwind CSS

**Props**:
- `portfolioId` (number): The ID of the portfolio
- `token` (string): Authentication token for private portfolios

**States**:
- `heatmapData`: The aggregated activity data from API
- `loading`: Loading state
- `error`: Error messages
- `hoveredDate`: Currently hovered date cell
- `hoveredData`: Activity data for hovered date

#### Integration

The component is integrated into the portfolio detail page:
- **Location**: `src/frontend/src/app/portfolios/[id]/page.js`
- **Placement**: After the "About" section, before "Projects" section
- **Styling**: Matches the existing portfolio page design with dark theme and blue accents

## Database Queries

The backend uses optimized database queries:

```python
# Fetch file activity
ProjectFile.objects.filter(
    project_id__in=project_ids
).values('project_id', 'project__name').annotate(
    date=TruncDate('created_at')
).values('date', 'project_id', 'project__name').annotate(
    count=Count('id')
)

# Fetch project creation activity
Project.objects.filter(
    id__in=project_ids
).values('id', 'name', 'created_at').annotate(
    date=TruncDate('created_at')
).values('date', 'id', 'name')
```

## Usage

### For End Users

1. Navigate to any portfolio detail page
2. Scroll down to see the "Activity Heatmap" section
3. Hover over any day to see:
   - Exact date
   - Number of activities
   - Intensity level
   - Project breakdown (which projects were active that day)
4. Use the legend to understand the color coding
5. View statistics: max daily activity, min daily activity, total days active

### For Developers

To customize the heatmap:

1. **Change activity sources**: Modify aggregation in `PortfolioActivityHeatmapView.get()`
2. **Adjust color ranges**: Update the `getActivityColor()` function in the component
3. **Modify date range calculation**: Update the calendar generation logic in `generateCalendar()`

## Performance Considerations

- **Database Optimization**: The backend uses `select_related()` and `prefetch_related()` to minimize query count
- **Frontend Rendering**: Calendar generation is O(n) where n is the number of days in the date range
- **API Response**: Typical response sizes are reasonable (< 100KB for a year of activity)

## Future Enhancements

Potential improvements for future versions:

1. **Commit-based activity**: When git commit data is available, use actual commit dates instead of file uploads
2. **Activity filtering**: Allow users to filter activity by specific projects or date ranges
3. **Export data**: Export heatmap data as CSV or image
4. **Custom color themes**: Allow users to customize the heatmap color scheme
5. **Activity types**: Show different icons/colors for different types of activity (commits, files, collaborations)
6. **Yearly comparison**: Show multiple years side-by-side for comparison
7. **Streak tracking**: Highlight consecutive days of activity

## Testing

### Manual Testing Steps

1. Create a portfolio with multiple projects
2. Add files to projects with various dates
3. Navigate to the portfolio detail page
4. Verify the heatmap displays:
   - Correct date range
   - Accurate activity counts
   - Proper color intensity
   - Correct project breakdown in tooltips
5. Test with empty portfolios (should show "No activity data")
6. Test with single-day activity
7. Verify responsive design on mobile/tablet/desktop

### API Testing

```bash
# Fetch heatmap data for a portfolio
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/portfolio/1/activity-heatmap/
```

## Privacy & Permissions

- **Public portfolios**: Anyone can view the activity heatmap
- **Private portfolios**: Only the portfolio owner (authenticated) can view the heatmap
- **Access control**: Returns 401 (unauthorized) or 404 (not found) for inaccessible portfolios

## File Changes Summary

### Backend Files Modified/Created

- `src/backend/app/views/portfolio_views.py`:
  - Added imports: `Count`, `F`, `Q`, `TruncDate`, `Cast`, `DateTimeField`, `timedelta`, `defaultdict`
  - Added `PortfolioActivityHeatmapView` class

- `src/backend/app/urls.py`:
  - Added import: `PortfolioActivityHeatmapView`
  - Added URL pattern: `path("portfolio/<int:pk>/activity-heatmap/", PortfolioActivityHeatmapView.as_view(), ...)`

### Frontend Files Modified/Created

- `src/frontend/src/components/PortfolioActivityHeatmap.js` (new file):
  - Custom heatmap component with calendar visualization

- `src/frontend/src/app/portfolios/[id]/page.js`:
  - Added import: `PortfolioActivityHeatmap`
  - Added component in left column after About section

## Browser Compatibility

- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support
- Mobile browsers: ✅ Full support (responsive)

## Styling Notes

The heatmap follows the existing design system:
- **Colors**: Blue gradient (#1e40af to #93c5fd) matching portfolio theme
- **Typography**: Uses existing font scales from Tailwind
- **Spacing**: Uses Tailwind spacing units (p-6, gap-4, etc.)
- **Dark theme**: Integrates with portfolio's dark UI (slate-800, slate-900 backgrounds)

## Troubleshooting

### Heatmap not showing data

1. Verify portfolio has projects with files
2. Check browser console for API errors
3. Verify backend is returning correct data via API endpoint
4. Check authentication token is valid for private portfolios

### Colors not displaying correctly

1. Ensure Tailwind CSS is properly configured
2. Clear browser cache and rebuild frontend
3. Check for CSS override conflicts in custom stylesheets

### Performance issues

1. If portfolio has thousands of days of activity, consider pagination
2. Implement server-side caching of heatmap data for frequently accessed portfolios
3. Use database indexing on `ProjectFile.created_at`

## Related Features

- Portfolio Statistics: `GET /api/portfolio/<id>/stats/`
- Project Details: `GET /api/project/<id>/`
- Portfolio Summary: Generated by LLM service based on projects
