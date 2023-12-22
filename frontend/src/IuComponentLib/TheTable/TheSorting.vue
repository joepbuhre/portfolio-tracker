<template>
    <button @click="doSorting(objectKey)">
        <span class="flex items-center gap-1 uppercase">
            {{ display.name }}
            <span
                :class="{
                    'text-slate-300': !(objectKey === srtVal),
                }"
                class="relative flex items-center justify-center gap-2"
            >
                <TheSortingIcon
                    :objectKey="objectKey"
                    :srtVal="srtVal"
                    :dir="dir"
                />
            </span>
        </span>
    </button>
</template>
<script setup lang="ts">
import TheSortingIcon from "./TheSortingIcon.vue";
import { HeaderValues } from "./types";
import { dir, srtVal, doSorting } from "./sorting";

defineProps<{
    objectKey: any;
    display: HeaderValues;
}>();
</script>
