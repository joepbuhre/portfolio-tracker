<template>
    <div ref="dropdown">
        <button @click="toggleDropdown">
            <FilterIcon :size="14" class="mr-1" />
        </button>
        <div>
            <div
                class="absolute left-0 top-[80%] flex items-center justify-center"
            >
                <!-- Dropdown menu -->
                <Transition
                    enter-active-class="ease duration-300"
                    leave-active-class="duration-300"
                    enter-from-class=" opacity-0"
                    leave-to-class=" opacity-0"
                >
                    <div
                        id="dropdown"
                        class="z-10 w-full rounded-lg bg-white p-3 shadow dark:bg-gray-700"
                        v-show="showFilter"
                    >
                        <ul
                            class="space-y-2 text-sm"
                            aria-labelledby="dropdownDefault"
                        >
                            <li class="flex items-center" v-for="val in vals">
                                <input
                                    :id="val"
                                    :name="val"
                                    v-model="selectedValues"
                                    type="checkbox"
                                    :value="val"
                                    class="text-primary-600 focus:ring-primary-500 dark:focus:ring-primary-600 h-4 w-4 rounded border-gray-300 bg-gray-100 focus:ring-2 dark:border-gray-500 dark:bg-gray-600 dark:ring-offset-gray-700"
                                    @change="
                                        emit('filterChange', selectedValues)
                                    "
                                />

                                <label
                                    :for="val"
                                    class="ml-2 text-sm font-medium text-gray-900 hover:cursor-pointer dark:text-gray-100"
                                >
                                    {{ val }}
                                </label>
                            </li>
                        </ul>
                        <button
                            @click="
                                selectedValues = [];
                                showFilter = false;
                                emit('filterChange', selectedValues);
                            "
                        >
                            clear
                        </button>
                    </div>
                </Transition>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { FilterIcon } from "lucide-vue-next";
import { computed, ref, watch } from "vue";
import { onClickOutside } from "@vueuse/core";
import { doFiltering } from "./filtering";

const dropdown = ref(null);

onClickOutside(dropdown, (event) => {
    showFilter.value = false;
});

const emit = defineEmits<{
    (e: "filterChange", filterValues: any[]): void;
}>();

const toggleDropdown = (e: Event) => {
    showFilter.value = !showFilter.value;
};

const showFilter = ref<boolean>(false);

const props = defineProps<{
    filterValues: string[];
}>();

const vals = computed(() => {
    return Array.from(new Set(props.filterValues)).sort();
});

const selectedValues = ref<string[]>([]);
</script>
