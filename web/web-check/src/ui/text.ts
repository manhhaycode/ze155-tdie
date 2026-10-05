// Every Vietnamese UI string of the overlay (PLAN-DOT1 §4.2.10). State button labels come from
// cut_states.json `label_vi`, device texts from devices.json; everything else lives here.

const NBSP = '\u00a0'

/** 2450 -> "2 450", -120 -> "−120" (grouping with a no-break space, as in the plan) */
export function fmtInt(v: number): string {
  const n = Math.round(v)
  const s = String(Math.abs(n)).replace(/\B(?=(\d{3})+(?!\d))/g, NBSP)
  return n < 0 ? `−${s}` : s
}

export const T = {
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
