function large(a, b, c) {
  let x = 10; // unused variable
  if (a > 0) {
    if (b > 0) {
      if (c > 0) {
        return a + b + c;
      }
    }
  }
  return 0;
}

// Another function with high complexity
function processData(data, options, callback) {
  if (!data) {
    return null;
  }

  if (options.validate) {
    if (!data.id) {
      throw new Error("Missing id");
    }
    if (!data.name) {
      throw new Error("Missing name");
    }
    if (!data.email) {
      throw new Error("Missing email");
    }
  }

  let result = {
    id: data.id,
    name: data.name,
    email: data.email,
  };

  if (options.transform) {
    if (options.uppercase) {
      result.name = result.name.toUpperCase();
    }
    if (options.lowercase) {
      result.email = result.email.toLowerCase();
    }
  }

  if (callback) {
    callback(result);
  }

  return result;
}

module.exports = { large, processData };
