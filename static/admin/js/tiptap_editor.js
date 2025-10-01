document.addEventListener('DOMContentLoaded', () => {
    // Find all textareas that should be replaced by a Tiptap editor
    const textareas = document.querySelectorAll('textarea[name="body"]');

    textareas.forEach(textarea => {
        const container = textarea.closest('.tiptap-container');
        if (!container) return;

        const editorElement = container.querySelector('.tiptap-editor');
        const toolbarElement = container.querySelector('.tiptap-toolbar');

        const editor = new tiptap.core.Editor({
            element: editorElement,
            extensions: [
                tiptap.starterKit.StarterKit,
            ],
            content: textarea.value,
            onUpdate: ({ editor }) => {
                // Sync the Tiptap content back to the hidden textarea
                textarea.value = editor.getHTML();
            },
        });

        // Basic Toolbar Example
        toolbarElement.innerHTML = `
            <button type="button" class="tiptap-button" onclick="event.preventDefault(); editor.chain().focus().toggleBold().run()">Bold</button>
            <button type="button" class="tiptap-button" onclick="event.preventDefault(); editor.chain().focus().toggleItalic().run()">Italic</button>
            <button type="button" class="tiptap-button" onclick="event.preventDefault(); editor.chain().focus().toggleStrike().run()">Strike</button>
            <button type="button" class="tiptap-button" onclick="event.preventDefault(); editor.chain().focus().setParagraph().run()">Paragraph</button>
            <button type="button" class="tiptap-button" onclick="event.preventDefault(); editor.chain().focus().toggleHeading({ level: 1 }).run()">H1</button>
            <button type="button" class="tiptap-button" onclick="event.preventDefault(); editor.chain().focus().toggleHeading({ level: 2 }).run()">H2</button>
            <button type="button" class="tiptap-button" onclick="event.preventDefault(); editor.chain().focus().toggleBulletList().run()">Bullet List</button>
            <button type="button" class="tiptap-button" onclick="event.preventDefault(); editor.chain().focus().toggleOrderedList().run()">Ordered List</button>
        `;
    });
});
