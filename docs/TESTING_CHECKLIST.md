# Testing Checklist

## Installation Test
- [ ] Run `pip install -r requirements.txt`
- [ ] Verify all packages install without errors
- [ ] Run `streamlit run app.py`
- [ ] Verify app opens in browser at http://localhost:8501

## Basic Functionality
- [ ] See welcome screen with feature list
- [ ] Sidebar shows "Upload Python file or ZIP"
- [ ] No errors in console

## Single File Upload Test
- [ ] Click "Browse files" in sidebar
- [ ] Upload `sample_code.py`
- [ ] Click "Analyze Code" button
- [ ] See success message "Successfully parsed 1 file(s)"
- [ ] See file listed in sidebar under "Files"
- [ ] See metrics bar at top with counts

## Metrics Panel Test
- [ ] Verify "Functions" count shows correct number
- [ ] Verify "Classes" count shows correct number
- [ ] Verify "Methods" count shows correct number
- [ ] Verify "Total Nodes" is sum of above
- [ ] Verify "Max Call Depth" shows a number

## Call Tree Tab Test
- [ ] Click "Call Tree" tab
- [ ] See dropdown "Select root function"
- [ ] Select "main" from dropdown
- [ ] See hierarchical tree visualization
- [ ] Verify nodes are color-coded (blue/green/orange)
- [ ] Hover over nodes to see tooltips
- [ ] Verify tree shows main → create_animal → Dog/Cat

## Dependency Graph Tab Test
- [ ] Click "Dependency Graph" tab
- [ ] See interactive network graph
- [ ] Verify all functions and classes appear as nodes
- [ ] Verify edges connect related nodes
- [ ] Try dragging nodes around
- [ ] Try zooming in/out
- [ ] Verify colors: blue (functions), green (classes), orange (methods)

## Class Hierarchy Tab Test
- [ ] Click "Class Hierarchy" tab
- [ ] See class inheritance tree
- [ ] Verify Animal at top
- [ ] Verify Dog and Cat below Animal
- [ ] Hover over classes to see methods listed
- [ ] Verify red edges show inheritance

## Mind Map Tab Test
- [ ] Click "Mind Map" tab
- [ ] See dropdown "Select center node"
- [ ] Select different functions from dropdown
- [ ] Verify radial layout with center node in red
- [ ] Verify surrounding nodes show callers/callees
- [ ] Try selecting "main", "create_animal", "make_animals_speak"

## Metrics Tab Test
- [ ] Click "Metrics" tab
- [ ] See "Most Called Functions" list
- [ ] See "Most Dependencies" list
- [ ] See "Unused Functions" section
- [ ] Verify "unused_function" appears in unused list
- [ ] See "Complexity Statistics" with avg/max/min
- [ ] See "High Complexity Functions" if any

## Filter Features Test
- [ ] In sidebar, see "Filter by file" dropdown
- [ ] Select "sample_code.py"
- [ ] Verify visualizations update to show only that file
- [ ] Change "Max call depth" slider
- [ ] Verify call tree respects depth limit

## Search Feature Test
- [ ] In sidebar, see "Node Search" section
- [ ] Type "Dog" in search box
- [ ] See matching results appear
- [ ] Select "Dog" from results
- [ ] See "Node Details" expander appear
- [ ] Verify details show: name, type, file, line, parameters
- [ ] Verify "Called by" and "Calls" lists appear
- [ ] Click "View source code" expander
- [ ] See source code snippet

## Multi-File Test (Optional)
- [ ] Create a .zip file containing both sample_code.py and sample_utils.py
- [ ] Upload the .zip file
- [ ] Click "Analyze Code"
- [ ] Verify both files appear in sidebar
- [ ] Verify cross-file relationships are tracked
- [ ] Use "Filter by file" to switch between files

## Error Handling Test
- [ ] Create a .py file with syntax errors
- [ ] Upload and analyze
- [ ] Verify warning message appears
- [ ] Click "View parsing errors" expander
- [ ] See which files failed and why
- [ ] Verify valid files still process correctly

## Edge Cases Test
- [ ] Verify recursive_fibonacci shows self-loop or recursive call
- [ ] Verify nested functions are handled
- [ ] Verify methods show parent class
- [ ] Verify inheritance edges are red
- [ ] Verify call edges are gray

## Performance Test
- [ ] Upload file, analyze
- [ ] Switch between tabs multiple times
- [ ] Verify no re-parsing occurs (should be instant)
- [ ] Change filters
- [ ] Verify updates are fast

## UI/UX Test
- [ ] All text is readable
- [ ] No overlapping elements
- [ ] Graphs fit in viewport
- [ ] Tooltips appear on hover
- [ ] Buttons respond to clicks
- [ ] Dropdowns work correctly
- [ ] Sliders move smoothly

## Documentation Test
- [ ] Open README.md - verify it's comprehensive
- [ ] Open QUICKSTART.md - verify it's clear
- [ ] Open PROJECT_SUMMARY.md - verify it's detailed
- [ ] Check docstrings in any .py file - verify Google style

## Final Verification
- [ ] No errors in browser console
- [ ] No errors in terminal/command prompt
- [ ] All features work as described
- [ ] App is responsive and interactive
- [ ] Ready for production use

---

## If Any Test Fails
1. Check terminal for error messages
2. Check browser console (F12) for JavaScript errors
3. Verify all dependencies installed correctly
4. Verify Python version is 3.8+
5. Try restarting the Streamlit server

## Success Criteria
All checkboxes should be checked for full functionality verification.
