<template>
    <div class="my-10 flex gap-5">
        <div class="w-1/6">
            <button
                class="flex w-full gap-3 rounded-md bg-slate-100 px-2 py-2 text-left font-bold text-blue-900"
            >
                <span class="w-1/12"><UserCircle /></span><span> Test</span>
            </button>
        </div>
        <div class="w-full">
            <h4 class="text-lg font-bold">Profile</h4>
            <h5 class="text-sm text-gray-600">
                This information will be displayed publicly so be careful what
                you share.
            </h5>
            <hr class="my-6" />
        </div>
    </div>
</template>

<script setup lang="ts">
import { UserCircle } from "lucide-vue-next";
</script>
