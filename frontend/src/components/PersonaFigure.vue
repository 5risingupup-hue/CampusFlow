<template>
  <div class="persona-frame" :class="[persona, size]">
    <div class="persona-card" />
    <div class="persona-shadow" />

    <div class="person-stage">
      <div class="hair" />
      <div class="head" />
      <div class="face">
        <span class="eye" />
        <span class="eye" />
      </div>
      <div v-if="persona === 'teacher'" class="glasses">
        <span />
        <span />
      </div>
      <div class="neck" />
      <div class="body" />
      <div class="arm arm-left" />
      <div class="arm arm-right" />
      <div class="leg leg-left" />
      <div class="leg leg-right" />
      <div class="accessory" />
      <div v-if="persona === 'counselor'" class="lanyard" />
      <div v-if="persona === 'male_student'" class="strap" />
      <div v-if="persona === 'teacher'" class="book-mark" />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  persona: 'male_student' | 'female_student' | 'counselor' | 'teacher'
  size?: 'hero' | 'compact'
}>()
</script>

<style scoped>
.persona-frame {
  --frame-width: 230px;
  --frame-height: 290px;
  --stage-scale: 1;
  position: relative;
  width: var(--frame-width);
  height: var(--frame-height);
}

.persona-frame.compact {
  --frame-width: 96px;
  --frame-height: 122px;
  --stage-scale: 0.4;
}

.persona-card {
  position: absolute;
  inset: 0;
  border-radius: calc(24px * var(--stage-scale));
  background: linear-gradient(180deg, #efc79f, #ddb489);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.18),
    0 20px 40px rgba(120, 80, 40, 0.14);
}

:root[data-theme='dark'] .persona-card {
  background: linear-gradient(180deg, #d0a67f, #b78b63);
}

.persona-shadow {
  position: absolute;
  inset: auto 18px 12px;
  height: calc(18px * var(--stage-scale));
  border-radius: 999px;
  background: color-mix(in srgb, var(--cf-ink) 18%, transparent);
  filter: blur(10px);
}

.person-stage {
  position: absolute;
  left: 50%;
  bottom: calc(12px * var(--stage-scale));
  width: 180px;
  height: 240px;
  transform: translateX(-50%) scale(var(--stage-scale));
  transform-origin: center bottom;
}

.hair,
.head,
.face,
.body,
.arm,
.leg,
.accessory,
.lanyard,
.strap,
.book-mark {
  position: absolute;
}

.hair {
  left: 50%;
  top: 6px;
  width: 86px;
  height: 74px;
  margin-left: -43px;
  border-radius: 48px 48px 34px 34px;
  z-index: 1;
}

.head {
  left: 50%;
  top: 24px;
  width: 68px;
  height: 72px;
  margin-left: -34px;
  border-radius: 50%;
  background: #f5ccaa;
  z-index: 2;
}

.face {
  left: 50%;
  top: 56px;
  display: flex;
  gap: 12px;
  margin-left: -14px;
  z-index: 4;
}

.eye {
  width: 6px;
  height: 8px;
  border-radius: 999px;
  background: #243248;
}

.glasses {
  left: 50%;
  top: 50px;
  display: flex;
  gap: 8px;
  margin-left: -22px;
  z-index: 5;
}

.glasses span {
  width: 18px;
  height: 16px;
  border: 3px solid #334155;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.2);
}

.glasses::after {
  content: "";
  position: absolute;
  left: 17px;
  top: 7px;
  width: 10px;
  height: 3px;
  background: #334155;
}

.neck {
  left: 50%;
  top: 92px;
  width: 18px;
  height: 16px;
  margin-left: -9px;
  border-radius: 8px;
  background: #f1c39d;
  z-index: 1;
}

.body {
  left: 50%;
  top: 102px;
  width: 96px;
  height: 102px;
  margin-left: -48px;
  border-radius: 30px 30px 24px 24px;
  z-index: 1;
}

.arm {
  top: 110px;
  width: 22px;
  height: 100px;
  border-radius: 999px;
  background: #f1c39d;
  z-index: 0;
}

.arm-left {
  left: 26px;
  transform: rotate(6deg);
}

.arm-right {
  right: 26px;
  transform: rotate(-6deg);
}

.leg {
  top: 196px;
  width: 28px;
  height: 66px;
  border-radius: 999px;
  z-index: 0;
}

.leg-left {
  left: 62px;
}

.leg-right {
  right: 62px;
}

.accessory {
  z-index: 5;
}

.male_student .hair {
  background: #26334c;
  width: 78px;
  height: 54px;
  margin-left: -39px;
  border-radius: 28px 28px 18px 18px;
}

.male_student .body {
  background: linear-gradient(180deg, #4371c9, #2f57a9);
}

.male_student .leg {
  background: #2b3348;
}

.male_student .accessory {
  left: 50%;
  top: 150px;
  width: 56px;
  height: 74px;
  margin-left: -28px;
  border-radius: 18px;
  background: #3c73d4;
  box-shadow: inset 0 -10px 0 rgba(15, 42, 102, 0.16);
}

.male_student .strap {
  left: 54px;
  top: 114px;
  width: 12px;
  height: 76px;
  border-radius: 999px;
  background: #1f3f79;
  transform: rotate(8deg);
  z-index: 3;
}

.female_student .hair {
  background: #d97a30;
  box-shadow: inset 0 -10px 0 rgba(112, 58, 20, 0.16);
}

.female_student .body {
  background: linear-gradient(180deg, #8d7a6f, #7c6a60);
}

.female_student .leg {
  background: #343c55;
}

.female_student .accessory {
  left: 50%;
  top: 146px;
  width: 72px;
  height: 52px;
  margin-left: -36px;
  border-radius: 18px;
  background: #f0e9dc;
  border: 4px solid #4d463b;
  box-shadow: inset 0 0 0 6px #faf5ec;
}

.female_student .accessory::before,
.female_student .accessory::after {
  content: "";
  position: absolute;
  top: 15px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 3px solid #4d463b;
}

.female_student .accessory::before {
  left: 15px;
}

.female_student .accessory::after {
  right: 15px;
}

.counselor .hair {
  background: #242834;
  width: 92px;
  height: 78px;
  margin-left: -46px;
}

.counselor .body {
  width: 102px;
  margin-left: -51px;
  background: #242834;
  border: 6px solid #d45151;
}

.counselor .leg {
  background: #2f3447;
}

.counselor .accessory {
  right: 20px;
  top: 138px;
  width: 28px;
  height: 66px;
  border-radius: 14px;
  background: #36425e;
}

.counselor .lanyard {
  left: 50%;
  top: 108px;
  width: 30px;
  height: 42px;
  margin-left: -15px;
  border-radius: 14px;
  border: 4px solid rgba(255, 255, 255, 0.2);
  border-top-color: transparent;
  z-index: 4;
}

.teacher .hair {
  background: #6f5444;
  width: 88px;
  height: 58px;
  margin-left: -44px;
  border-radius: 32px 32px 22px 22px;
}

.teacher .head {
  top: 26px;
}

.teacher .body {
  width: 102px;
  margin-left: -51px;
  background: linear-gradient(180deg, #3257a8, #2c4f97);
}

.teacher .leg {
  background: #313752;
}

.teacher .accessory {
  right: 16px;
  top: 158px;
  width: 28px;
  height: 46px;
  border-radius: 12px;
  background: #f3f2ec;
  box-shadow: inset 0 -8px 0 rgba(186, 180, 164, 0.4);
}

.teacher .book-mark {
  right: 22px;
  top: 162px;
  width: 8px;
  height: 18px;
  background: #e4a631;
  border-radius: 0 0 6px 6px;
  z-index: 6;
}

@media (max-width: 760px) {
  .persona-frame.hero {
    --frame-width: 184px;
    --frame-height: 234px;
    --stage-scale: 0.8;
  }
}
</style>
