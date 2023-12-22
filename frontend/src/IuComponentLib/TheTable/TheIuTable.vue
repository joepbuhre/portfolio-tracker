<template>
    <table
        class="w-full border border-solid text-left text-sm text-gray-700 rtl:text-right dark:text-gray-400"
    >
        <thead
            class="bg-gray-50 text-xs text-gray-900 dark:bg-gray-700 dark:text-gray-400"
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
                            :display="<HeaderValues>display"
                        />
                        <span v-else>
                            {{ (display as HeaderValues).name }}
                        </span>
                    </th>
                </slot>
            </tr>
        </thead>
        <tbody>
            <tr v-if="(getRows ?? []).length === 0">
                <td :colspan="Object.keys(getHeaders).length" class="m-auto">
                    <div
                        class="my-10 flex w-full items-center justify-center gap-3"
                    >
                        <Loader2Icon class="animate-spin" />
                        Loading ...
                    </div>
                </td>
            </tr>
            <slot
                v-for="row in getRows"
                name="tr"
                :value="row"
                :headers="getHeaders"
            >
                <tr
                    class="border-b bg-white text-left dark:border-gray-700 dark:bg-gray-800"
                >
                    <slot
                        v-for="(display, key) of getHeaders"
                        name="td"
                        :value="row[key as keyof typeof row]"
                    >
                        <td class="px-6 py-2">
                            {{
                                formattedValue(
                                    display as HeaderValues,
                                    row,
                                    key,
                                )
                            }}
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
import { filterFunction } from "./filtering";
import { Loader2Icon } from "lucide-vue-next";

const props = withDefaults(
    defineProps<{
        headers?: Header;
        rows: Row[];
        sortingEnabled?: boolean;
    }>(),
    {
        sortingEnabled: true,
    },
);

const getHeaders = computed((): Header => {
    if (props.headers) {
        return props.headers;
    } else {
        const slots = getCurrentInstance()?.slots;
        if (slots === undefined) return {};

        const columns =
            slots
                .default?.()
                .filter((el) => el.type == TheColumn)
                .map((el): [any, HeaderValues] => {
                    return [
                        el.props?.["column-name"],
                        {
                            name:
                                el.props?.["display-name"] ??
                                el.props?.["column-name"],
                            formatter: el.props?.["formatter"],
                        },
                    ];
                }) ?? [];

        return Object.fromEntries(columns);
    }
});

const getRows = computed((): Row[] => {
    // if (srtVal.value === null) {
    //     return props.rows;
    // } else {
    return props.rows.sort(sortFunction).filter(filterFunction);
    // }
});

const formattedValue = (
    display: HeaderValues,
    row: Row,
    key: keyof typeof row,
): string => {
    if (display.formatter) {
        return display.formatter.format(row[key]);
    } else {
        return row[key];
    }
};

onMounted(() => {});
</script>
