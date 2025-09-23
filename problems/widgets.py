from django.contrib.admin.widgets import FilteredSelectMultiple

class CustomFilteredSelectMultiple(FilteredSelectMultiple):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        print("--- Parameter Values for create_option ---")
        print(f"Name (type: {type(name).__name__}): {name}")
        print(f"Value (type: {type(value).__name__}): {value}")
        print(f"Label (type: {type(label).__name__}): {label}")
        print(f"Selected (type: {type(selected).__name__}): {selected}")
        print(f"Index (type: {type(index).__name__}): {index}")
        print(f"Subindex (type: {type(subindex).__name__}): {subindex}")
        print(f"Attrs (type: {type(attrs).__name__}): {attrs}")
        print("------------------------------------------")
        
        if value:
            try:
                pass
                # Retrieve the Problem instance associated with the option value
                # self.choices.queryset provides access to the related model's queryset
                pk = value.value
                instance = self.choices.queryset.get(pk=pk)
                #Assuming 'tags' is a ManyToManyField, join the tag names
                tags_str = ", ".join([tag.name for tag in instance.tags.all()])
                print(f"Tags for Problem '{instance.title}': {tags_str}")
                option['attrs']['data-tags'] = tags_str
                print(option)
            except self.choices.queryset.model.DoesNotExist:
                pass
    
        return option