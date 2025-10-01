'use strict';
{
    function initializeUniqueTagSelector() {
        const taggedProblemGroup = document.querySelector('#taggedproblem_set-group');
        if (!taggedProblemGroup) return;

        function updateTagOptions() {
            const tagSelects = taggedProblemGroup.querySelectorAll('select[id^="id_taggedproblem_set-"][id$="-tag"]');
            const selectedValues = new Set();

            // First, find all selected tags
            tagSelects.forEach(select => {
                if (select.value) {
                    selectedValues.add(select.value);
                }
            });

            // Now, disable/enable options in all dropdowns
            tagSelects.forEach(currentSelect => {
                const currentSelectValue = currentSelect.value;
                currentSelect.querySelectorAll('option').forEach(option => {
                    // Don't disable the empty option or the currently selected option for this specific dropdown
                    if (option.value && option.value !== currentSelectValue && selectedValues.has(option.value)) {
                        option.hidden = true;
                    } else {
                        option.hidden = false;
                    }
                });
            });
        }

        // Use a mutation observer to handle dynamically added forms (when clicking "Add another Tagged Problem")
        const observer = new MutationObserver(mutations => {
            mutations.forEach(mutation => {
                if (mutation.type === 'childList') {
                    taggedProblemGroup.querySelectorAll('select[id$="-tag"]').forEach(select => {
                        select.removeEventListener('change', updateTagOptions); // Avoid duplicate listeners
                        select.addEventListener('change', updateTagOptions);
                    });
                    updateTagOptions();
                }
            });
        });

        observer.observe(taggedProblemGroup.querySelector('tbody'), { childList: true });

        // Initial setup
        taggedProblemGroup.querySelectorAll('select[id$="-tag"]').forEach(select => {
            select.addEventListener('change', updateTagOptions);
        });
        updateTagOptions();
    }

    document.addEventListener('DOMContentLoaded', function() {
        initializeUniqueTagSelector();
    });
}


