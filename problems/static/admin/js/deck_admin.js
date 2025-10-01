document.addEventListener('DOMContentLoaded', function() {
    // The inline group for DeckTagFilter has a specific ID pattern
    const deckTagFilterGroup = document.getElementById('decktagfilter_set-group');

    if (!deckTagFilterGroup) {
        return; // Exit if the inline group is not on the page
    }

    function updateTagOptions() {
        // Find all select elements for tags within the inline group
        const tagSelects = deckTagFilterGroup.querySelectorAll('select[id$="-tag"]');
        
        // Get all currently selected tag values, excluding empty ones
        const selectedValues = Array.from(tagSelects)
            .map(select => select.value)
            .filter(value => value);

        // Iterate over each select box again to update its options
        tagSelects.forEach(function(currentSelect) {
            const currentValue = currentSelect.value;
            const options = currentSelect.querySelectorAll('option');

            options.forEach(function(option) {
                const isSelectedElsewhere = selectedValues.includes(option.value);
                const isOwnSelection = option.value === currentValue;

                option.style.display = (isSelectedElsewhere && !isOwnSelection) ? 'none' : '';
            });
        });
    }

    updateTagOptions();

    deckTagFilterGroup.addEventListener('change', function(e) {
        if (e.target && e.target.matches('select[id$="-tag"]')) {
            updateTagOptions();
        }
    });

    const addRowLink = deckTagFilterGroup.querySelector('.add-row a');
    if (addRowLink) {
        addRowLink.addEventListener('click', () => setTimeout(updateTagOptions, 50));
    }
});