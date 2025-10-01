import { Editor } from 'https://esm.sh/@tiptap/core'
import StarterKit from 'https://esm.sh/@tiptap/starter-kit'
import Link from 'https://esm.sh/@tiptap/extension-link'
import Image from 'https://esm.sh/@tiptap/extension-image'

/**
 * A simple function to get a cookie by name.
 * We need this to get the CSRF token.
 * @param {string} name The name of the cookie to retrieve.
 * @returns {string|null} The cookie value or null if not found.
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Creates and returns a file input element configured for image uploads.
 * @param {string} uploadUrl - The URL to post the image to.
 * @param {Editor} editor - The Tiptap editor instance.
 * @returns {HTMLInputElement}
 */
function createImageUploadInput(uploadUrl, editor) {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    input.style.display = 'none';

    input.onchange = () => {
        const file = input.files[0];
        if (!file) {
            console.log('Image upload: No file selected.');
            input.remove(); // Clean up if no file is chosen
            return;
        }
        console.log('Image upload: File selected:', file.name);

        const formData = new FormData();
        formData.append('image', file);

        const csrfToken = getCookie('csrftoken');
        console.log('Image upload: Preparing to upload to:', uploadUrl);
        console.log('Image upload: Using CSRF Token:', csrfToken);

        fetch(uploadUrl, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
            },
            body: formData,
            // Note: No 'Content-Type' header, browser sets it with boundary for multipart/form-data
        })
        .then(response => {
            console.log('Image upload: Received response from server:', response);
            if (!response.ok) {
                // If we get an error response (e.g., 404, 500, 403), throw an error to be caught by .catch()
                throw new Error(`Server responded with status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Image upload: Parsed JSON data:', data);
            if (data.url) {
                console.log('Image upload: Success! Inserting image with URL:', data.url);
                editor.chain().focus().setImage({ src: data.url }).run();
            } else {
                throw new Error(data.error || 'JSON response did not contain a URL.');
            }
        })
        .catch(error => {
            console.error('Error uploading image:', error);
            alert('Error uploading image.');
        })
        .finally(() => {
            // Clean up the input element
            console.log('Image upload: Cleaning up file input.');
            input.remove();
        });
    };
    return input;
}

// Create an object to hold all editor instances, keyed by textarea ID.
const TiptapEditors = {};
function initializeTiptapEditors() {
    console.log("Tiptap module: DOMContentLoaded event fired. Initializing editors...");

    // Find all hidden textareas within our Tiptap containers
    const textareas = document.querySelectorAll('.tiptap-container textarea[name$="body"]');
    console.log(`Found ${textareas.length} Tiptap-enabled textareas to process.`);

    textareas.forEach(textarea => {
        console.group(`Initializing Tiptap for textarea #${textarea.id}`);
        console.log("Textarea element:", textarea);

        const container = textarea.closest('.tiptap-container');
        if (!container) {
            console.error('Could not find a parent `.tiptap-container`. Aborting initialization for this textarea.');
            console.groupEnd();
            return;
        }

        const editorElement = container.querySelector('.tiptap-editor');
        const toolbarElement = container.querySelector('.tiptap-toolbar');

        const editor = new Editor({
            element: editorElement,
            extensions: [
                // Configure StarterKit and pass link options to it
                StarterKit.configure({
                    // This configures the Link extension within StarterKit
                    link: { openOnClick: false },
                }),
                // Add the Image extension here
                Image,
            ],
            // Use the content from the hidden textarea.
            content: textarea.value,
            onUpdate: ({ editor }) => {
                // Update all buttons' active states
                updateToolbarButtons(toolbarElement, editor);

                // Sync the Tiptap content back to the hidden textarea on every change.
                const html = editor.getHTML();
                if (textarea.value !== html) {
                    textarea.value = html;
                }
            },
            onSelectionUpdate: ({ editor }) => {
                // Also update button states when the user's selection changes
                // (e.g., clicking on an image).
                updateToolbarButtons(toolbarElement, editor);
            },
        });
        console.log("Tiptap editor instance created.");

        TiptapEditors[textarea.id] = editor;
        console.log("Textarea id:", textarea.id);

        // --- Toolbar Setup ---
        const buttons = [
            { command: 'toggleBold', label: 'Bold' },
            { command: 'toggleItalic', label: 'Italic' },
            { command: 'toggleStrike', label: 'Strike' },
            {
                command: 'deleteSelection', // Command to remove the selected node
                label: 'Remove Image',
                activeCheck: 'image', // Becomes active when an image is selected
            },
            { command: 'setParagraph', label: 'Paragraph' },
            { command: 'toggleHeading', args: { level: 1 }, label: 'H1' },
            { command: 'toggleHeading', args: { level: 2 }, label: 'H2' },
            { command: 'toggleBulletList', label: 'Bullet List' },
            { command: 'toggleOrderedList', label: 'Ordered List' },
        ];

        // --- Custom "Link Problem" Button ---
        const popupUrl = container.dataset.popupUrl; // Reads `data-popup-url`
        console.log(`Checking for Problem Link feature... data-popup-url: "${popupUrl}"`);
        if (popupUrl) {
            const linkButton = document.createElement('button');
            linkButton.type = 'button';
            linkButton.className = 'tiptap-button';
            linkButton.title = 'Link to a Problem';
            linkButton.textContent = 'Link Problem';
            linkButton.addEventListener('click', (e) => {
                e.preventDefault();
                // This is the function Django's admin uses to open popups.
                // It requires a dummy link element with the correct href and id.
                const dummyLink = document.createElement('a');
                dummyLink.href = popupUrl;
                dummyLink.id = `lookup_${textarea.id}`; // e.g., lookup_id_body
                return window.showRelatedObjectLookupPopup(dummyLink);
            });
            toolbarElement.appendChild(linkButton);
            console.log('-> "Link Problem" button added.');
        } else {
            console.log('-> "Link Problem" button not added (no data-popup-url found).');
        }

        // --- Custom "Add Image" Button ---
        const imageUploadUrl = container.dataset.imageUploadUrl;
        console.log(`Checking for Image Upload feature... data-image-upload-url: "${imageUploadUrl}"`);
        if (imageUploadUrl) {
            const imageButton = document.createElement('button');
            imageButton.type = 'button';
            imageButton.className = 'tiptap-button';
            imageButton.title = 'Add Image';
            imageButton.innerHTML = '🖼️'; // Or use a proper icon
            imageButton.addEventListener('click', (e) => {
                e.preventDefault();
                console.log('Image upload: "Add Image" button clicked.');
                const input = createImageUploadInput(imageUploadUrl, editor);
                document.body.appendChild(input);
                input.click();
            });
            toolbarElement.appendChild(imageButton);
            console.log('-> "Add Image" button added.');
        }
        buttons.forEach(config => {
            const button = document.createElement('button');
            button.type = 'button';
            button.className = 'tiptap-button';
            button.title = config.title || config.label;
            // Use icon if available, otherwise fall back to label
            button.innerHTML = config.icon || config.label;

            button.addEventListener('click', (e) => {
                e.preventDefault();
                if (config.action) {
                    config.action(); // Execute custom action
                } else if (config.command) {
                    // Execute a standard Tiptap command
                    editor.chain().focus()[config.command](config.args).run();
                }
            });
            toolbarElement.appendChild(button);
        });
        console.log("Standard toolbar buttons created.");
        console.groupEnd();
    });
}
function updateToolbarButtons(toolbarElement, editor) {
    toolbarElement.querySelectorAll('button[data-command]').forEach(button => {
        const command = button.dataset.command;
        const activeCheck = button.dataset.activeCheck || command;
        if (editor.isActive(activeCheck)) {
            button.classList.add('is-active');
        } else {
            button.classList.remove('is-active');
        }
    });
}

// Run the initialization script once the DOM is ready.
window.addEventListener('DOMContentLoaded', initializeTiptapEditors);

// Export the editor registry for other modules to use.
export { TiptapEditors };
