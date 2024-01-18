<template>
    <div class="relative max-w-sm">
        <div
            ref="datepicker"
            v-if="showPicker"
            class="absolute inset-y-0 start-0 flex items-center ps-3"
        >
            <div
                class="datepicker datepicker-dropdown dropdown active datepicker-orient-bottom datepicker-orient-left absolute left-10 top-10 z-50 block pt-2"
            >
                <div
                    class="datepicker-picker z-50 inline-block rounded-lg bg-white p-4 shadow-lg dark:bg-gray-700"
                >
                    <div class="datepicker-header">
                        <div
                            class="datepicker-title bg-white px-2 py-3 text-center font-semibold dark:bg-gray-700 dark:text-white"
                            style="display: none"
                        ></div>
                        <div
                            class="datepicker-controls mb-2 flex justify-between"
                        >
                            <button
                                type="button"
                                class="prev-btn rounded-lg bg-white p-2.5 text-lg text-gray-500 hover:bg-gray-100 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-gray-200 dark:bg-gray-700 dark:text-white dark:hover:bg-gray-600 dark:hover:text-white"
                                @click="setMonth('down')"
                            >
                                <ChevronLeftIcon /></button
                            ><TheDateDropdown>
                                {{
                                    dateformatter({
                                        month: "long",
                                        year: "2-digit",
                                    })(
                                        dates.find(
                                            (el) => el.current_month === true,
                                        )?.date,
                                    )
                                }}</TheDateDropdown
                            >
                            <button
                                type="button"
                                class="next-btn rounded-lg bg-white p-2.5 text-lg text-gray-500 hover:bg-gray-100 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-gray-200 dark:bg-gray-700 dark:text-white dark:hover:bg-gray-600 dark:hover:text-white"
                                @click="setMonth('up')"
                            >
                                <ChevronRightIcon />
                            </button>
                        </div>
                    </div>
                    <div class="datepicker-main p-1">
                        <div class="datepicker-view flex">
                            <div class="days">
                                <div class="days-of-week mb-1 grid grid-cols-7">
                                    <span
                                        v-for="weekname in getWeekNames"
                                        class="dow h-6 text-center text-sm font-medium leading-6 text-gray-500 dark:text-gray-400"
                                        >{{ weekname }}</span
                                    >
                                </div>
                                <div
                                    class="datepicker-grid grid w-64 grid-cols-7"
                                >
                                    <span
                                        v-for="date in dates"
                                        class="datepicker-cell day prev block flex-1 cursor-pointer rounded-lg border-0 text-center text-sm font-semibold leading-9 text-gray-500 text-gray-900 hover:bg-gray-100 dark:text-white dark:hover:bg-gray-600"
                                        :class="{
                                            'opacity-30': !date.current_month,
                                            'bg-blue-400': date.is_today,
                                        }"
                                        :date="date.date.toISOString()"
                                        @click="selectDate(date)"
                                        >{{ date.number }}</span
                                    >
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="datepicker-footer">
                        <div
                            class="datepicker-controls mt-2 flex space-x-2 rtl:space-x-reverse"
                        >
                            <button
                                type="button"
                                class="button today-btn !bg-primary-700 dark:!bg-primary-600 hover:!bg-primary-800 dark:hover:!bg-primary-700 focus:!ring-primary-300 w-1/2 rounded-lg bg-blue-700 px-3 py-1 text-center text-sm font-medium text-white hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 dark:bg-blue-600 dark:hover:bg-blue-700"
                                @click="date = new Date().getTime()"
                            >
                                Today
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div
            class="flex w-full gap-2 rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-blue-500 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:placeholder-gray-400 dark:focus:border-blue-500 dark:focus:ring-blue-500"
        >
            <button @click="showPicker = !showPicker">
                <CalendarIcon />
            </button>
            <input
                datepicker
                datepicker-orientation="bottom right"
                type="text"
                placeholder="Select date"
                class="w-full"
                v-model="date"
            />
        </div>
    </div>
</template>
<script setup lang="ts">
import {
    ChevronLeftIcon,
    CalendarIcon,
    ChevronRightIcon,
} from "lucide-vue-next";
import { computed, onMounted, ref, watch } from "vue";
import TheDateDropdown from "./TheDateDropdown.vue";
import { onClickOutside } from "@vueuse/core";

const showPicker = ref<boolean>(false);

const date = ref<number>(new Date().getTime());

interface DateObject {
    date: Date;
    number: number;
    current_month: boolean;
    is_today: boolean;
    date_name: number;
}

const dates = computed(() => {
    let original_month = new Date(date.value);
    let start_month = new Date(date.value);
    let end_month = new Date(date.value);
    start_month.setDate(1);
    end_month.setDate(0);
    end_month.setMonth(end_month.getMonth() + 1);

    console.log(start_month.getUTCDay());
    console.log(end_month.toISOString());

    // Minus 6 days to ensure we got all weekdays.
    start_month.setDate(start_month.getDate() - 6);

    let range = [...Array(45).keys()].map((el) => {
        // Build object with a date
        // Then add a date (otherwise loop will go haywire)
        let obj: DateObject = {
            date: new Date(start_month),
            number: start_month.getDate(),
            current_month:
                original_month.getUTCMonth() === start_month.getUTCMonth(),
            is_today: original_month.getDate() === start_month.getDate(),
            date_name: start_month.getDay(),
        };
        start_month.setDate(start_month.getDate() + 1);

        return obj;
    });

    let returns = range
        .filter(
            // @ts-ignore
            (el) => el.date >= range.find((el) => el.date_name === 1)?.date,
        )
        .splice(0, 35);
    return returns;
});

const dates2 = computed(() => {
    return date.value;
});

const getWeekNames = computed(() => {
    return ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"];
});

const selectDate = (date: (typeof dates.value)[0]) => {
    console.log(date);
};

const dateformatter = (options: Intl.DateTimeFormatOptions = {}) => {
    return new Intl.DateTimeFormat("en-US", options).format;
};

const setMonth = (dir: "up" | "down") => {
    console.log("clicking");
    let direction = dir === "up" ? 1 : -1;
    let dt = new Date(date.value);
    dt.setMonth(dt.getMonth() + direction);

    date.value = dt.getTime();
};

//
const datepicker = ref<HTMLElement | null>(null);
onClickOutside(datepicker, () => {
    showPicker.value = false;
});
</script>
