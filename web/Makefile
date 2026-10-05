# ZE 155 web, Đợt 1 build (PLAN-DOT1 §3.5).   Usage: make -C web all   (cwd = web/)
#
# export   background Blender (-b --factory-startup) reads the SAVED ../out/ze155_anim.blend, never saves it
# compress gltf-transform 4.5.1: dedup --materials false -> prune --keep-leaves true -> meshopt --level high
# analyze  node tools/check_glb.mjs analyze   -> build/reports/glb_analysis.json
# data     python3 tools/make_data.py         -> build/data/*.json (5 files)
# verify   node tools/check_glb.mjs verify    -> build/reports/check.json (exit 1 on any failure, no publish)
# publish  copy models + data into web-check/public/
#
# Only one `make export` at a time (both write build/raw). Unsaved edits in an open Blender session
# are NOT exported: the export reads the .blend as last saved on disk.

BLENDER ?= /Applications/Blender.app/Contents/MacOS/Blender
BLEND   := ../out/ze155_anim.blend
GT      := tools/node_modules/.bin/gltf-transform
FILES   := line interior
STRIP   := perl -pe 's/\e\[[0-9;]*m//g'
NOW      = $$(perl -MTime::HiRes=time -e 'printf "%.3f", time')
TLOG    := build/reports/timings.txt

# stages must run in order (and never two exports at once), even under make -j
.NOTPARALLEL:

.PHONY: all export compress analyze data verify publish clean distclean deps compare-drafts verify-negative test-search

all: export compress analyze data verify publish
	@echo "MAKE ALL DONE"; cat $(TLOG)

deps: tools/node_modules/.package-lock.json

tools/node_modules/.package-lock.json: tools/package.json tools/package-lock.json
	cd tools && npm ci --no-audit --no-fund

export:
	mkdir -p build/raw build/reports
	@: > $(TLOG)
	stat -f '%m %z' $(BLEND) > build/reports/blend_before.txt
	@t0=$(NOW); \
	$(BLENDER) -b --factory-startup --python-exit-code 1 $(BLEND) --python tools/export_glb.py -- \
	  --rules web/dot1/selection-rules.json --file all --out web/build/raw --report web/build/reports/export.json --tris \
	  > build/reports/export.log 2>&1; rc=$$?; \
	echo "export $$(perl -e "printf '%.2f', $(NOW) - $$t0") s" >> $(TLOG); \
	grep -E '^(EXPORTED|EXPORT DONE)' build/reports/export.log; \
	if [ $$rc -ne 0 ]; then tail -30 build/reports/export.log; exit $$rc; fi
	stat -f '%m %z' $(BLEND) > build/reports/blend_after.txt
	diff build/reports/blend_before.txt build/reports/blend_after.txt

compress: deps
	mkdir -p build/tmp build/models build/reports
	@t0=$(NOW); \
	for f in $(FILES); do \
	  $(GT) dedup   build/raw/$$f.glb   build/tmp/$$f.1.glb  --materials false --vertex-layout separate > build/tmp/$$f.dedup.log 2>&1 && \
	  $(GT) prune   build/tmp/$$f.1.glb build/tmp/$$f.2.glb  --keep-leaves true --keep-attributes false --vertex-layout separate > build/tmp/$$f.prune.log 2>&1 && \
	  $(GT) meshopt build/tmp/$$f.2.glb build/models/$$f.glb --level high --vertex-layout separate > build/tmp/$$f.meshopt.log 2>&1 && \
	  $(GT) validate build/models/$$f.glb 2>&1 | $(STRIP) > build/reports/$$f.validate.txt && \
	  $(GT) validate build/raw/$$f.glb 2>&1 | $(STRIP) > build/reports/$$f.raw.validate.txt || { cat build/tmp/$$f.*.log; exit 1; }; \
	  echo "compressed $$f: $$(stat -f %z build/raw/$$f.glb) -> $$(stat -f %z build/models/$$f.glb) B"; \
	done; \
	echo "compress $$(perl -e "printf '%.2f', $(NOW) - $$t0") s" >> $(TLOG)

analyze: deps
	@t0=$(NOW); node tools/check_glb.mjs analyze || exit 1; \
	echo "analyze $$(perl -e "printf '%.2f', $(NOW) - $$t0") s" >> $(TLOG)

data:
	@t0=$(NOW); python3 tools/make_data.py || exit 1; \
	echo "data $$(perl -e "printf '%.2f', $(NOW) - $$t0") s" >> $(TLOG)

verify: deps
	@t0=$(NOW); node tools/check_glb.mjs verify || exit 1; \
	echo "verify $$(perl -e "printf '%.2f', $(NOW) - $$t0") s" >> $(TLOG)

publish:
	test -f build/reports/check.json && grep -q '"ok": true' build/reports/check.json
	mkdir -p web-check/public/models web-check/public/data
	cp build/models/line.glb build/models/interior.glb web-check/public/models/
	cp build/data/devices.json build/data/node_map.json build/data/cut_states.json build/data/rotors.json build/data/materials.json web-check/public/data/
	@echo "published: $$(stat -f '%N %z' web-check/public/models/*.glb | tr '\n' ' ')"

# task A4: build/data must equal web/dot1/*.dot1.json except the intended differences listed in make_data.py
compare-drafts:
	python3 tools/make_data.py --compare dot1

# task A5 negative test: a renamed node in a copy of cut_states.json must make verify exit 1
verify-negative:
	rm -rf build/tmp/neg && mkdir -p build/tmp/neg && cp build/data/*.json build/tmp/neg/
	python3 -c "import json; p='build/tmp/neg/cut_states.json'; d=json.load(open(p)); h=d['states']['CUT_Z_BARREL']['hide']; h[0]=h[0]+'_typo'; json.dump(d, open(p, 'w'))"
	@if node tools/check_glb.mjs verify --data build/tmp/neg --report build/tmp/neg/check.json; then echo "NEGATIVE TEST FAILED: verify accepted a renamed node"; exit 1; else echo "NEGATIVE TEST OK: verify rejected the renamed node"; fi

# task A6: accent-insensitive device search ("xi lanh b3", "xi lanh", "bom", ...)
test-search:
	node tools/test_search.mjs

clean:
	rm -rf build/tmp

distclean: clean
	rm -rf build/raw build/models build/data build/reports
