'use strict';
{
    const SelectBox = {
        cache: {},
        init: function(id) {
            const box = document.getElementById(id);
            SelectBox.cache[id] = [];
            const cache = SelectBox.cache[id];
            for (const node of box.options) {
                // Add the data-tags attribute to the cache
                const dataTags = node.getAttribute('data-tags');
                cache.push({value: node.value, text: node.text, displayed: 1, dataTags: dataTags});
            }
        },
        redisplay: function(id) {
            // Repopulate HTML select box from cache
            const box = document.getElementById(id);
            const scroll_value_from_top = box.scrollTop;
            box.innerHTML = '';
            for (const node of SelectBox.cache[id]) {
                if (node.displayed) {
                    const new_option = new Option(node.text, node.value, false, false);
                    // Re-apply the data-tags attribute from the cache
                    if (node.dataTags) {
                        new_option.setAttribute('data-tags', node.dataTags);
                    }
                    // Shows a tooltip when hovering over the option
                    new_option.title = node.text;
                    box.appendChild(new_option);
                }
            }
            box.scrollTop = scroll_value_from_top;
        },
        filter: function(id, text) {
            // 1. Split the input and filter out any empty strings that may result.
            const tokens = text.toLowerCase().split(/\s*,\s*|\s+/).filter(token => token);
            
            const includeTokens = tokens.filter(token => !token.startsWith('-'));
            const excludeTokens = tokens.filter(token => token.startsWith('-')).map(token => token.substring(1));

            for (const node of SelectBox.cache[id]) {
                node.displayed = 1;
                const node_tags_array = node.dataTags ? node.dataTags.toLowerCase().split(/\s*,\s*/) : [];

                // 2. Add an explicit check to ensure the tag array is not empty.
                // This prevents the filter from incorrectly passing an empty tag list.
                const filtered_tags = node_tags_array.filter(tag => tag);

                // Check for inclusion (must have ALL include tags)
                let hasAllIncludeTags = true;
                if (includeTokens.length > 0) {
                    for (const token of includeTokens) {
                        if (!filtered_tags.includes(token)) {
                            hasAllIncludeTags = false;
                            break;
                        }
                    }
                }

                // Check for exclusion (must have NONE of the exclude tags)
                let hasNoExcludeTags = true;
                for (const token of excludeTokens) {
                    if (filtered_tags.includes(token)) {
                        hasNoExcludeTags = false;
                        break;
                    }
                }

                if (!hasAllIncludeTags || !hasNoExcludeTags) {
                    node.displayed = 0;
                }
            }
            SelectBox.redisplay(id);
        },
        get_hidden_node_count(id) {
            const cache = SelectBox.cache[id] || [];
            return cache.filter(node => node.displayed === 0).length;
        },
        delete_from_cache: function(id, value) {
            let delete_index = null;
            const cache = SelectBox.cache[id];
            for (const [i, node] of cache.entries()) {
                if (node.value === value) {
                    delete_index = i;
                    break;
                }
            }
            cache.splice(delete_index, 1);
        },
        add_to_cache: function(id, option) {
            SelectBox.cache[id].push({value: option.value, text: option.text, displayed: 1});
        },
        cache_contains: function(id, value) {
            // Check if an item is contained in the cache
            for (const node of SelectBox.cache[id]) {
                if (node.value === value) {
                    return true;
                }
            }
            return false;
        },
        move: function(from, to) {
            const from_box = document.getElementById(from);
            for (const option of from_box.options) {
                const option_value = option.value;
                if (option.selected && SelectBox.cache_contains(from, option_value)) {
                    SelectBox.add_to_cache(to, {value: option_value, text: option.text, displayed: 1});
                    SelectBox.delete_from_cache(from, option_value);
                }
            }
            SelectBox.redisplay(from);
            SelectBox.redisplay(to);
        },
        move_all: function(from, to) {
            const from_box = document.getElementById(from);
            for (const option of from_box.options) {
                const option_value = option.value;
                if (SelectBox.cache_contains(from, option_value)) {
                    SelectBox.add_to_cache(to, {value: option_value, text: option.text, displayed: 1});
                    SelectBox.delete_from_cache(from, option_value);
                }
            }
            SelectBox.redisplay(from);
            SelectBox.redisplay(to);
        },
        sort: function(id) {
            SelectBox.cache[id].sort(function(a, b) {
                a = a.text.toLowerCase();
                b = b.text.toLowerCase();
                if (a > b) {
                    return 1;
                }
                if (a < b) {
                    return -1;
                }
                return 0;
            } );
        },
        select_all: function(id) {
            const box = document.getElementById(id);
            for (const option of box.options) {
                option.selected = true;
            }
        }
    };
    window.SelectBox = SelectBox;
}
