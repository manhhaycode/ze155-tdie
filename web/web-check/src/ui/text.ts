// Every UI string of the overlay (PLAN-DOT1 §4.2.10), Vietnamese `T` and Japanese `T_JA`. Vietnamese state
// labels come from cut_states.json `label_vi`, device texts from devices.json; the Japanese ones from
// `T_JA.states` / `T_JA.sections` and /i18n/devices.ja.json (see i18n.ts).

const NBSP = '\u00a0'

/** 2450 -> "2 450", -120 -> "−120" (grouping with a no-break space, as in the plan) */
export function fmtInt(v: number): string {
  const n = Math.round(v)
  const s = String(Math.abs(n)).replace(/\B(?=(\d{3})+(?!\d))/g, NBSP)
  return n < 0 ? `−${s}` : s
}

export const T = {
  docTitle: 'ZE 155 – dây chuyền (Đợt 1)',
  lang: 'Ngôn ngữ',
  brand: 'Logo khách hàng TOYOBO',
  /** overrides of devices.json section names / cut_states.json labels (empty: the data is Vietnamese) */
  sections: {} as Record<string, string>,
  states: {} as Record<string, string>,
  tree: {
    title: 'Thiết bị',
    search: 'Tìm thiết bị (gõ không dấu cũng được)…',
    searchLabel: 'Tìm thiết bị',
    clear: 'Xoá ô tìm',
    noResult: 'Không tìm thấy thiết bị nào.',
    count: (n: number, total: number) => (n === total ? `${total} thiết bị` : `${n}/${total} thiết bị`),
    hasInterior: 'Có phần bên trong (xem bằng mặt cắt)',
    collapse: 'Thu gọn danh sách',
    expand: 'Mở danh sách thiết bị',
  },
  info: {
    empty: 'Chọn một thiết bị trong danh sách bên trái hoặc bấm lên mô hình.',
    group: 'Nhóm',
    function: 'Chức năng',
    details: 'Chi tiết',
    connects: 'Nối với',
    size: 'Kích thước (mm)',
    sizeAxes: 'D × C × S',
    part: (name: string) => `Chi tiết: ${name}`,
    inside: 'Nằm bên trong – mở một mặt cắt để xem',
    synthetic: 'Thiết bị tổng hợp: chưa có mô tả chi tiết.',
    zoom: 'Phóng to',
    deselect: 'Bỏ chọn',
    hint: 'Bấm đúp hoặc F: phóng to · Alt + bấm: chọn một chi tiết · Esc: bỏ chọn',
    /** "Nối với" targets that are not devices (review M6) */
    otherTargets: { ctx_floor: 'Sàn nhà xưởng' } as Record<string, string>,
  },
  toolbar: {
    states: 'Trạng thái',
    freeAxis: 'Trục cắt',
    // FREE axes use the Blender names of the state buttons ("Y = 0", "Z = 1 200"), review I3
    axisHint: {
      X: 'X: dọc dòng chảy – mặt cắt ngang, như "X = 2 450"',
      Y: 'Y: ngang máy – mặt cắt dọc đứng, như "Y = 0"',
      Z: 'Z: chiều cao – mặt cắt nằm ngang, như "Z = 1 200"',
    } as Record<'X' | 'Y' | 'Z', string>,
    freeOffset: 'Vị trí',
    freeValue: (axis: string, mm: number) => `${axis} = ${fmtInt(mm)} mm`,
    freeFlip: 'Lật phía giữ',
    freeKeep: (axis: string, flip: boolean, mm: number) => `Đang giữ phần ${axis} ${flip ? '≥' : '≤'} ${fmtInt(mm)} mm`,
    capLegend: 'Màu nắp cắt',
    rotor: 'Quay',
    rotorOff: 'Tắt',
    rotorSlow: (k: number) => `Chậm ${k}×`,
    rotorReal: 'Thực tế',
    rotorBadge: (rpm: number, mode: 'off' | 'slow' | 'real', k: number) =>
      mode === 'off' ? 'Đã tắt quay' : mode === 'slow' ? `Vít ${fmtInt(rpm)} vòng/phút – hiển thị chậm ${k}×` : `Vít ${fmtInt(rpm)} vòng/phút – tốc độ thực`,
    resetView: 'Về góc nhìn của trạng thái',
    loadingInterior: 'Đang tải phần bên trong…',
    busy: 'Đang chuyển trạng thái…',
  },
  caps: {
    steel: 'Thép (vân chéo)',
    screw: 'Trục vít',
    rubber: 'Cao su',
    insulation: 'Cách nhiệt',
    melt: 'Nhựa nóng chảy',
  } as Record<string, string>,
}

export type Texts = typeof T

export const T_JA: Texts = {
  docTitle: 'ZE 155 – 押出ライン（第1期）',
  lang: '言語',
  brand: 'TOYOBO ロゴ',
  sections: {
    base: 'ベースフレーム',
    drive: '駆動部',
    feed: '原料供給',
    barrel: 'バレルとスクリュー',
    vacuum: '真空脱気',
    melt: '溶融樹脂ライン',
    die: 'Tダイ',
    control: '制御・ケーブル',
    util: '圧縮空気・冷却水',
    context: 'ロール・シート・計測（周辺設備）',
  },
  states: {
    FULL: '全体（断面なし）',
    CUT_FEED: '供給部 縦断面 (Y = 0)',
    CUT_Z_BARREL: 'バレル上半分カット (Z = 1 200)',
    CUT_X2450: 'B3 横断面 (X = 2 450)',
    CUT_X4120: '真空ベント2 横断面 (X = 4 120)',
    FREE: '自由断面',
  },
  tree: {
    title: '機器',
    search: '機器名・ID で検索…',
    searchLabel: '機器を検索',
    clear: '検索をクリア',
    noResult: '該当する機器はありません。',
    count: (n: number, total: number) => (n === total ? `${total} 件` : `${n}/${total} 件`),
    hasInterior: '内部構造あり（断面で表示）',
    collapse: 'リストを折りたたむ',
    expand: '機器リストを開く',
  },
  info: {
    empty: '左のリストから機器を選ぶか、モデルをクリックしてください。',
    group: 'グループ',
    function: '機能',
    details: '詳細',
    connects: '接続先',
    size: '寸法 (mm)',
    sizeAxes: '長さ × 高さ × 奥行',
    part: (name: string) => `部品: ${name}`,
    inside: '内部にあります – 断面を開いて表示してください',
    synthetic: '集約機器：詳細な説明はまだありません。',
    zoom: 'ズーム',
    deselect: '選択解除',
    hint: 'ダブルクリックまたは F: ズーム · Alt + クリック: 部品を選択 · Esc: 選択解除',
    otherTargets: { ctx_floor: '工場床面' },
  },
  toolbar: {
    states: '表示状態',
    freeAxis: '断面軸',
    axisHint: {
      X: 'X: 流れ方向 – 横断面（例 "X = 2 450"）',
      Y: 'Y: 機械の幅方向 – 縦断面（例 "Y = 0"）',
      Z: 'Z: 高さ方向 – 水平断面（例 "Z = 1 200"）',
    },
    freeOffset: '位置',
    freeValue: (axis: string, mm: number) => `${axis} = ${fmtInt(mm)} mm`,
    freeFlip: '残す側を反転',
    freeKeep: (axis: string, flip: boolean, mm: number) => `${axis} ${flip ? '≥' : '≤'} ${fmtInt(mm)} mm 側を表示中`,
    capLegend: '断面の色',
    rotor: '回転',
    rotorOff: '停止',
    rotorSlow: (k: number) => `${k}倍スロー`,
    rotorReal: '実速度',
    rotorBadge: (rpm: number, mode: 'off' | 'slow' | 'real', k: number) =>
      mode === 'off' ? '回転停止中' : mode === 'slow' ? `スクリュー ${fmtInt(rpm)} rpm – ${k}倍スロー表示` : `スクリュー ${fmtInt(rpm)} rpm – 実速度`,
    resetView: 'この状態の視点に戻す',
    loadingInterior: '内部モデルを読み込み中…',
    busy: '状態を切り替え中…',
  },
  caps: {
    steel: '鋼（斜線）',
    screw: 'スクリュー',
    rubber: 'ゴム',
    insulation: '断熱材',
    melt: '溶融樹脂',
  },
}
