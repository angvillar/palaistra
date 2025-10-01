import { TiptapEditors } from './tiptap_editor.js';

console.log('related_popup.js: Module loaded. Overriding dismissRelatedLookupPopup.');
// Store the original function so we can call it for other popups.
const originalDismissRelatedLookupPopup = window.dismissRelatedLookupPopup;

// This function is called by the popup window when an item is selected.
// We are overriding the default Django admin function.
window.dismissRelatedLookupPopup = function(win, chosenId) {
    console.log('related_popup.js: Custom dismissRelatedLookupPopup called.');
    console.log(`- Window Name: ${win.name}, Chosen ID: ${chosenId}`);

    const name = win.name; // e.g., 'lookup_id_body'
    // Django's popup mechanism can add a suffix like '__1' to the window name. We need to remove it.
    const elemId = name.replace(/^lookup_/, '').split('__')[0]; // e.g., 'id_body'
    console.log(`- Derived Element ID: ${elemId}`);

    // Check if a Tiptap editor instance exists for this element ID.
    if (TiptapEditors && TiptapEditors[elemId]) {
        console.log(`- SUCCESS: Found Tiptap editor for ID "${elemId}".`);
        const editor = TiptapEditors[elemId];
        const url = `/problems/${chosenId}/`; // Construct the problem's public URL
        const linkText = `Problem #${chosenId}`;
        console.log(`- Inserting link: href="${url}", text="${linkText}"`);

        // Use the Tiptap editor's API to insert a link.
        editor.chain().focus().extendMarkRange('link').setLink({ href: url }).insertContent(linkText).run();

        win.close();
    } else {
        console.log(`- Tiptap editor for ID "${elemId}" not found. Falling back to original Django function.`);
        // Fallback to original Django behavior for other popups (e.g., standard ForeignKey lookups)
        originalDismissRelatedLookupPopup.apply(window, arguments);
    }
};
