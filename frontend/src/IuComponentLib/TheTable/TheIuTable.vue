<template>
    <table
        class="w-full text-sm text-left rtl:text-right text-gray-700 dark:text-gray-400 border border-solid"
    >
        <thead
            class="text-xs text-gray-900 bg-gray-50 dark:bg-gray-700 dark:text-gray-400"
        >
            <tr class="relative">
                <slot name="default">
                    <th
                        scope="col"
                        class="px-6 py-3 text-left uppercase"
                        v-for="(display, key) of getHeaders"
                    >
                        <TheSorting
                            v-if="props.sortingEnabled"
                            :object-key="key"
                            :display="(display as HeaderValues)"
                        />
                        <span v-else>
                            {{ (display as HeaderValues).name }}
                        </span>
                    </th>
                </slot>
               
            </tr>
        </thead>
        <tbody>
            <slot
                v-for="row in getRows"
                name="tr"
                :value="row"
                :headers="getHeaders"
            >
                <tr
                    class="bg-white border-b dark:bg-gray-800 dark:border-gray-700 text-left"
                >
                    <slot
                        v-for="(display, key) of getHeaders"
                        name="td"
                        :value="row[key as keyof typeof row]"
                    >
                        <td class="px-6 py-2">
                            {{ formattedValue((display as HeaderValues), row, key) }}
                        </td>
                    </slot>
                </tr>
            </slot>
        </tbody>
    </table>
</template>

<script setup lang="ts">
import { computed, getCurrentInstance, onMounted, ref } from "vue";
import type { Header, HeaderValues, Row } from "./types";
import { dir, sortFunction, srtVal } from "./sorting";
import TheSorting from "./TheSorting.vue";
import TheColumn from "./TheColumn.vue";

const props = withDefaults(
    defineProps<{
        headers?: Header;
        rows: Row[];
        sortingEnabled?: boolean;
    }>(),
    {
        sortingEnabled: true,
    }
);

const getHeaders = computed((): Header => {
    if(props.headers) {
        return props.headers;
    } else {
        const slots = getCurrentInstance()?.slots;
        if(slots === undefined) return {};

        const columns = slots.default?.().filter(el => el.type == TheColumn).map((el): [any, HeaderValues] => {
            return [
                el.props?.['column-name'], {
                    name: (el.props?.['display-name'] ?? el.props?.['column-name'] ),
                    formatter: el.props?.['formatter']
                }
            ]
        }) ?? []
        console.log(columns)
        return Object.fromEntries(columns) 
        
    }
});

const getRows = computed((): Row[] => {
    if (srtVal.value === null) {
        return props.rows;
    } else {
        return props.rows.sort(sortFunction);
    }
});

const formattedValue = (
    display: HeaderValues,
    row: Row,
    key: keyof typeof row
): string => {
    if (display.formatter) {
        return display.formatter.format(row[key]);
    } else {
        return row[key];
    }
};

onMounted(() => {
    
    
})

</script>
