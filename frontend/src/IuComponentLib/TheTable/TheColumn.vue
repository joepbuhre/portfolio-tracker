<template>
    <th
        scope="col"
        class="relative"
        :class="{
            'px-6 py-3 text-left uppercase': !reset,
        }"
    >
        <span class="flex items-center">
            <TheFilter
                v-if="props.filterValues"
                :filter-values="props.filterValues"
                @filter-change="filterChange"
            />
            <TheSorting
                v-if="sortingEnabled"
                :object-key="columnName"
                :display="{
                    name: displayName,
                    formatter: formatter,
                }"
            />
            <span v-else>
                {{ displayName }}
            </span>
        </span>
    </th>
</template>

<script setup lang="ts">
import type { HeaderValues, Row } from "./types";
import TheSorting from "./TheSorting.vue";
import { FilterIcon } from "lucide-vue-next";
import TheFilter from "./TheFilter.vue";
import { doFiltering } from "./filtering";

const props = withDefaults(
    defineProps<{
        columnName: string;
        displayName: string;
        sortingEnabled?: boolean;
        formatter?: HeaderValues["formatter"];
        reset?: boolean;
        filterValues?: string[];
    }>(),
    {
        sortingEnabled: true,
        reset: false,
    },
);

const filterChange = (vals: any[]) => {
    doFiltering(props.columnName, vals);
};
</script>
