<template>
    <!-- <button
                                type="button"
                                class="view-switch rounded-lg bg-white px-5 py-2.5 text-sm font-semibold text-gray-900 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-gray-200 dark:bg-gray-700 dark:text-white dark:hover:bg-gray-600"
                            >
                               </button -->
    <div class="relative">
        <button
            id="dropdownDefaultButton"
            data-dropdown-toggle="dropdown"
            class="view-switch relative flex rounded-lg bg-white px-5 py-2.5 text-sm font-semibold text-gray-900 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-gray-200 dark:bg-gray-700 dark:text-white dark:hover:bg-gray-600"
            type="button"
            @click="showDropdown = !showDropdown"
        >
            <slot></slot>
        </button>

        <!-- Dropdown menu -->
        <div
            id="dropdown"
            v-if="showDropdown"
            class="absolute z-10 w-44 divide-y divide-gray-100 rounded-lg bg-white shadow dark:bg-gray-700"
        >
            <ul
                class="py-2 text-sm text-gray-700 dark:text-gray-200"
                aria-labelledby="dropdownDefaultButton"
            >
                <li v-for="month in months">
                    <a
                        href="#"
                        class="block px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-600 dark:hover:text-white"
                        >{{ month }}</a
                    >
                </li>
            </ul>
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";

const showDropdown = ref<boolean>(false);

const months = computed(() => {
    let dt = new Date();

    dt.setMonth(dt.getMonth() - 4);

    console.log(dt);

    let months = [...Array(11).keys()].map((el) => {
        let fm = new Intl.DateTimeFormat("en-US", {
            month: "long",
            year: "2-digit",
        });
        let returns = fm.format(dt);
        dt.setMonth(dt.getMonth() + 1);

        return returns;
    });

    return months;
});
</script>
