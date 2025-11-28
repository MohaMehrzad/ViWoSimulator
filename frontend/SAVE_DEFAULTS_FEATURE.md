# Save Defaults Feature

## Overview
This feature allows users to save their current simulation parameters as custom defaults that persist across browser sessions. The saved defaults will automatically load when the application starts, making it easy to maintain preferred configurations.

## Features

### 🎯 Floating Action Button (FAB)
- **Location**: Bottom-right corner of the screen
- **Always Visible**: Accessible from any section of the simulator
- **Visual Indicator**: Shows a green checkmark when custom defaults are saved
- **Smooth Animations**: Modern, polished UI with fade and slide transitions

### 💾 Save Current Parameters
- Click the FAB to open the actions panel
- Click "Save Current as Default" to persist all current parameters
- Includes all simulation settings:
  - Core parameters (token price, marketing budget)
  - User acquisition settings (CAC, budget allocation)
  - Economic parameters (burn rate, buyback, reward allocation)
  - All module settings (Identity, Content, Advertising, Exchange, etc.)
  - Dynamic allocation settings
  - Liquidity and staking parameters
  - Growth scenario settings
  - Future module configurations

### 📂 Load Saved Defaults
- Load your saved defaults at any time
- Instantly restores all saved parameter values
- Useful for resetting to your preferred configuration after experimenting

### 🗑️ Clear Saved Defaults
- Remove saved defaults when no longer needed
- Confirmation dialog prevents accidental deletion
- Returns to using application's built-in defaults

### 🔄 Auto-Load on Startup
- Saved defaults automatically load when you open the simulator
- Seamless experience - your preferences are always ready
- New parameters added in updates are merged with your saved settings

## How to Use

### Saving Your Parameters
1. Adjust all simulation parameters to your preferred values
2. Click the floating 💾 button in the bottom-right corner
3. Click "Save Current as Default"
4. You'll see a success notification confirming the save
5. The FAB will now show a green ✓ indicator

### Loading Saved Defaults
1. Click the floating 💾 button
2. Click "Load Saved Defaults" (only visible if you have saved defaults)
3. All parameters will be restored to your saved values
4. You'll see a success notification

### Clearing Saved Defaults
1. Click the floating 💾 button
2. Click "Clear Saved Defaults" (only visible if you have saved defaults)
3. Confirm the action in the dialog
4. Saved defaults are removed
5. Next time you start the app, it will use built-in defaults

## Technical Details

### Storage Method
- Uses browser's `localStorage` API
- Storage key: `vcoin_simulator_defaults`
- Persists across browser sessions
- Survives page refreshes and browser restarts

### Data Format
- Saved as JSON string
- Complete `SimulationParameters` object
- Includes all configuration fields
- Forward-compatible with new parameters

### Auto-Load Behavior
- Loads saved defaults **after** component mounts on client-side (prevents hydration errors)
- Merges with built-in defaults (ensures new parameters are included)
- Gracefully handles errors if saved data is corrupted
- Falls back to built-in defaults if loading fails
- Hydration-safe: Server renders with defaults, client loads saved values after mount

### Browser Compatibility
- Works in all modern browsers (Chrome, Firefox, Safari, Edge)
- Requires JavaScript enabled
- Requires localStorage support (available in all modern browsers)

### Data Persistence
- Saved defaults persist indefinitely
- Not cleared by closing the browser
- Only cleared by:
  - Explicit "Clear Saved Defaults" action
  - Clearing browser data/cache
  - Browser's privacy settings

## UI/UX Features

### Visual Feedback
- ✅ Success notifications with slide-in animation
- 🟢 Green checkmark indicator when defaults are saved
- 🔄 Smooth rotation animation when opening/closing actions
- 📱 Responsive design works on all screen sizes

### Accessibility
- High-contrast colors for visibility
- Large, easy-to-click buttons
- Clear labels and descriptions
- Confirmation dialogs for destructive actions

### Performance
- Instant save/load operations
- No network requests required
- Minimal performance impact
- Efficient local storage usage

## Troubleshooting

### Saved Defaults Not Loading
- Check if browser's localStorage is enabled
- Check browser privacy settings
- Try clearing browser cache and saving again
- Check browser console for error messages

### Cannot Save Defaults
- Ensure localStorage quota is not exceeded
- Check browser's privacy/incognito mode settings
- Verify JavaScript is enabled
- Try a different browser

### Defaults Cleared Unexpectedly
- Check if browser is set to clear data on exit
- Verify browser privacy settings
- Check if using incognito/private mode
- Ensure not using browser's "Clear Recent History"

## File Structure

```
Simulator/frontend/src/
├── components/
│   └── SaveDefaultButton.tsx       # Main save button component
├── hooks/
│   └── useSimulation.ts            # Updated with auto-load logic
├── app/
│   ├── page.tsx                    # Integrated save button
│   └── globals.css                 # Added animations
└── types/
    └── simulation.ts                # Parameter types
```

## Code Examples

### Save Button Component
```tsx
<SaveDefaultButton 
  parameters={simulation.parameters}
  onLoadSavedDefaults={simulation.updateParameters}
/>
```

### Check for Saved Defaults
```typescript
const hasSaved = localStorage.getItem('vcoin_simulator_defaults') !== null;
```

### Manual Load
```typescript
const saved = localStorage.getItem('vcoin_simulator_defaults');
if (saved) {
  const params = JSON.parse(saved);
  simulation.updateParameters(params);
}
```

## Future Enhancements
- Export saved defaults as downloadable JSON file
- Import defaults from file
- Multiple saved configuration slots
- Share configurations via URL
- Cloud sync across devices (requires backend)
- Named configuration presets

## Support
For issues or questions about this feature:
1. Check browser console for error messages
2. Verify localStorage is enabled
3. Try clearing and re-saving defaults
4. Contact development team with error details

