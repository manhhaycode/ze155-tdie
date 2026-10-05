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
  /** state button tooltips (PLAN-FLOW §4.1); Vietnamese ones come from cut_states.json tooltip_vi */
  stateTips: {} as Record<string, string>,
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
    freeAxis: 'Hướng cắt',
    // PLAN-FLOW §4.1: the buttons say the cut direction; the Blender axis letter (review I3) stays in the tooltip
    axisLabel: { X: 'Cắt ngang', Y: 'Bổ dọc', Z: 'Cắt nằm' } as Record<'X' | 'Y' | 'Z', string>,
    axisHint: {
      X: 'Trục X (dọc dòng chảy): cắt ngang máy, nhìn vào lát cắt ngang',
      Y: 'Trục Y: bổ dọc máy, nhìn từ bên hông',
      Z: 'Trục Z (chiều cao): cắt nằm ngang, nhìn từ trên xuống',
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
  /** PLAN-FLOW §4.2: colour row of the FLOW state */
  flow: {
    color: 'Màu',
    colorLabel: 'Tô màu dòng nhựa',
    phase: 'Pha',
    heat: 'Nhiệt độ',
    phaseHint: 'Màu theo trạng thái vật liệu: hạt rắn, nhựa chảy, tấm PET',
    heatHint: 'Màu theo nhiệt độ đặt của từng vùng (giả định)',
    pellet: 'Hạt rắn',
    melt: 'Nhựa chảy',
    sheet: 'Tấm PET',
    assumed: '* giả định',
    assumedHint: 'Nhiệt độ là nhiệt độ đặt của vùng, lấy từ thiết kế mô phỏng; hình minh hoạ, không phải tính toán CFD',
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
    FULL: '全体',
    CUT_FEED: '投入ホッパー',
    CUT_Z_BARREL: 'バレル内部',
    CUT_X2450: 'スクリュー断面',
    CUT_X4120: '脱気部の断面',
    FLOW: '工程：ペレット→フィルム',
    FREE: '自由断面',
  },
  stateTips: {
    FULL: 'ライン全体（断面なし）',
    CUT_FEED: 'ホッパーと投入口を縦に切断し、ペレットがバレルへ落ちる経路を表示（Y = 0）',
    CUT_Z_BARREL: 'バレル上半分を外し、回転する2本のスクリューを表示（Z = 1 200）',
    CUT_X2450: 'B3 バレルの横断面：8の字の穴と噛み合う2本のスクリュー（X = 2 450 mm）',
    CUT_X4120: 'B5 の第2真空ベントの横断面：水分を吸い出す部分（X = 4 120 mm）',
    FLOW: 'ライン全体を縦に切断し、ペレットが溶けてフィルムになるまでを表示（Y = 0）',
    FREE: '切断方向と位置を自由に選択',
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
    freeAxis: '切断方向',
    axisLabel: { X: '横断', Y: '縦断', Z: '水平' },
    axisHint: {
      X: 'X 軸（流れ方向）：機械を横に切断し、横断面を表示',
      Y: 'Y 軸：機械を縦に切断し、側面から表示',
      Z: 'Z 軸（高さ）：水平に切断し、上から表示',
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
  flow: {
    color: '色',
    colorLabel: '樹脂の色分け',
    phase: '相',
    heat: '温度',
    phaseHint: '材料の状態で色分け：ペレット、溶融樹脂、PETシート',
    heatHint: '各ゾーンの設定温度で色分け（仮定）',
    pellet: 'ペレット',
    melt: '溶融樹脂',
    sheet: 'PETシート',
    assumed: '* 仮定',
    assumedHint: '温度は各ゾーンの設定温度（シミュレーション設計値）。説明用の図で、CFD 計算ではありません',
  },
  caps: {
    steel: '鋼（斜線）',
    screw: 'スクリュー',
    rubber: 'ゴム',
    insulation: '断熱材',
    melt: '溶融樹脂',
  },
}
