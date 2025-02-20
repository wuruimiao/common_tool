import csv


class CsvRecord:
    def __init__(self, delimiter=",") -> None:
        self._deli = delimiter
        self._cache = {}

    def _refresh_cache(self, csv_name):
        # lock
        with open(csv_name) as f:
            self._cache[csv_name] = f.readlines()

    def _get_primary_key(self, line):
        fields = line.split(self._deli)
        return fields[0]

    def get_by_key(self, csv_name: str, key: str):
        self._refresh_cache(csv_name)
        for item in self._cache[csv_name]:
            if key == self._get_primary_key(item):
                return item
        return None

    def exist(self, csv_name: str, key: str) -> bool:
        result = self.get_by_key(csv_name, key)
        return result is not None

    def new(self, csv_name: str, key: str, fields):
        self._refresh_cache(csv_name)
        with open(csv_name, "a") as f:
            f.write("\n")
            fields = self._deli.join(fields)
            f.write(f"{key}\t{fields}")

    def all(self, csv_name: str):
        with open(csv_name) as f:
            reader = csv.DictReader(f, delimiter=self._deli)
            result = []
            for line in reader:
                result.append(line)
        return result

    def all_group_by_key(self, csv_name: str, key_name="", key_func=None):
        data = self.all(csv_name)
        result = {}
        for item in data:
            if key_name == "":
                _key = key_func(item)
            else:
                _key = item[key_name]
            result[_key] = item
        return result
