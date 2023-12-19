<template>
    <th
        scope="col"
        :class="{
            'px-6 py-3 text-left uppercase': !reset
        }"
    >
        <TheSorting
            v-if="sortingEnabled"
            :object-key="columnName"
            :display="{
                name: displayName,
                formatter: formatter
            }"
        />
        <span v-else>
            {{ displayName }}
        </span>
    </th>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import type { Header, HeaderValues, Row } from "./types";
import { direction } from "./enums";
import { dir, sortFunction, srtVal } from "./sorting";
import TheSorting from "./TheSorting.vue";

const props = withDefaults(
    defineProps<{
        columnName: string;
        displayName: string;
        sortingEnabled?: boolean;
        formatter?: HeaderValues['formatter']
        reset?: boolean
    }>(),
    {
        sortingEnabled: true,
        reset: false
    }
);
</script>
