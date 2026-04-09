# NeuralBlitz C Implementation — Makefile
CC      ?= gcc
CFLAGS  ?= -std=c11 -Wall -Wextra -Wpedantic -O2
LDFLAGS ?= -lm
PREFIX  ?= /usr/local

INCLUDE_DIR = include
SRC_DIR     = src
BUILD_DIR   = build
TEST_DIR    = tests

SOURCES = $(wildcard $(SRC_DIR)/*.c)
OBJECTS = $(patsubst $(SRC_DIR)/%.c,$(BUILD_DIR)/%.o,$(SOURCES))
LIBRARY = $(BUILD_DIR)/libneuralblitz.a
TEST    = $(BUILD_DIR)/test_neuralblitz

.PHONY: all clean test install

all: $(LIBRARY) $(TEST)

$(BUILD_DIR):
	@mkdir -p $(BUILD_DIR)

$(BUILD_DIR)/%.o: $(SRC_DIR)/%.c | $(BUILD_DIR)
	@echo "  CC  $<"
	@$(CC) $(CFLAGS) -I$(INCLUDE_DIR) -c $< -o $@

$(LIBRARY): $(OBJECTS)
	@echo "  AR  $@"
	@ar rcs $@ $^

$(TEST): $(TEST_DIR)/test_neuralblitz.c $(LIBRARY)
	@echo "  CC  $< -> $@"
	@$(CC) $(CFLAGS) -I$(INCLUDE_DIR) $< -L$(BUILD_DIR) -lneuralblitz -lm -o $@

test: $(TEST)
	@echo ""
	@./$(TEST)

clean:
	@rm -rf $(BUILD_DIR)

install: $(LIBRARY)
	@mkdir -p $(PREFIX)/lib
	@mkdir -p $(PREFIX)/include/neuralblitz
	@cp $(LIBRARY) $(PREFIX)/lib/
	@cp $(INCLUDE_DIR)/neuralblitz/*.h $(PREFIX)/include/neuralblitz/

# Show build info
info:
	@echo "CC      = $(CC)"
	@echo "CFLAGS  = $(CFLAGS)"
	@echo "PREFIX  = $(PREFIX)"
	@echo "SOURCES = $(SOURCES)"
	@echo "OBJECTS = $(OBJECTS)"
