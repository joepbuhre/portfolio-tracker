<template>
    <TheDatePicker />
    <TheLoginModel v-if="showLogin" class="z-50" />
    <div class="fixed bottom-0 right-0 z-[99999] flex flex-col gap-2 pb-5 pr-5">
        <TheToast
            v-for="noti in not.get"
            @close="noti.delete()"
            :type="getToastType(noti.type)"
        >
            {{ noti.text }}
        </TheToast>
    </div>
    <TheHeader />
    <div class="px-10 pb-10">
        <router-view />
    </div>
</template>

<script setup lang="ts">
import TheHeader from "./components/TheHeader.vue";
import { useNotifications } from "./store/notifications";
import { TheToast, ToastType } from "@IuComponentLib/TheToast";
import { TheDatePicker } from "@IuComponentLib/TheDatePicker";
import { NotificationType } from "./enums/Notification";
import { computed, ref } from "vue";
import TheLoginModel from "@components/TheLoginModel.vue";
import { useMain } from "./store/main";

const main = useMain();
const showLogin = computed(() => main.getUserId === null);

const not = useNotifications();

const getToastType = (type: NotificationType): ToastType => {
    return type as unknown as ToastType;
};
</script>

<style lang="postcss">
body {
    @apply bg-slate-50 bg-opacity-10;
}
</style>
