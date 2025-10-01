document.addEventListener('DOMContentLoaded', function() {
    console.log('related_popup.js: DOM loaded, preparing to override dismissRelatedLookupPopup.');

    // Store the original function so we can call it for other popups.
    const originalDismissRelatedLookupPopup = window.dismissRelatedLookupPopup;

    // Override the function with our custom wrapper.
    window.dismissRelatedLookupPopup = function(win, chosenId, newRepr) {
        console.log('Custom dismissRelatedLookupPopup wrapper called.');
        console.log('Chosen ID:', chosenId);

        const name = win.name;
        console.log('Window name (should be element ID):', name);

        // Check if the popup was opened by our custom link helper.
        if (name.startsWith('lookup_id_body')) {
           console.log('Window name starts with "lookup_id_body". This is our custom helper.');
            // Since we know the static ID, we can hardcode it here.
            const elem = document.getElementById('lookup_id_body'); 
            console.log('Found element by hardcoded ID:', elem);
            if (elem && elem.dataset.id) {
                console.log('Element has data-id. This is our custom helper.');
                const textarea = document.getElementById(elem.dataset.id);
                console.log('Found textarea:', textarea);
                if (textarea) {
                    textarea.value += `[[problem:${chosenId}]]`;
                }
            }
            win.close();
        } else {
            console.log('Window name does not match. Falling back to original Django function.');
            // This is not our custom helper, so we let the original Django function do its job.
            // This is important for other related fields (like the source dropdowns) to work correctly.
            originalDismissRelatedLookupPopup(win, chosenId, newRepr);
        }
    };
});

