<template>
    <TransitionGroup
        enter-active-class="ease duration-500"
        leave-active-class="duration-500"
        enter-from-class="-rotate-180 opacity-0"
        leave-to-class="rotate-180 opacity-0"
    >
        <ArrowUpAZIcon
            class="ml-3 absolute"
            v-if="
                objectKey === srtVal &&
                dir === direction.ASC
            "
            :size="16"
        />
        <ArrowDownZAIcon
            class="ml-3 absolute"
            v-if="
                objectKey === srtVal &&
                dir === direction.DESC
            "
            :size="16"
        />
        <ChevronsUpDownIcon
            class="ml-3 absolute"
            v-if="objectKey !== srtVal"
            :size="16"
        />
    </TransitionGroup>
</template>

<script setup lang="ts">
import { direction } from './enums';
import { ArrowUpAZIcon, ChevronsUpDownIcon, ArrowDownZAIcon } from "lucide-vue-next";


defineProps<{
    objectKey: any,
    srtVal: any,
    dir: direction
}>()


</script>